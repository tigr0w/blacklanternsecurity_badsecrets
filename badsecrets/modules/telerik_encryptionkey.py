import re
import hmac
import base64
import urllib.parse
from Crypto.Cipher import AES
from Crypto.Protocol import KDF
from Crypto.Util.Padding import pad
from badsecrets.helpers import unpad
from badsecrets.base import BadsecretsBase
from badsecrets.helpers import Csharp_pbkdf1

telerik_hardcoded_salt = [58, 84, 91, 25, 10, 34, 29, 68, 60, 88, 44, 51, 1]


class Telerik_EncryptionKey_Exception(Exception):
    pass


class Telerik_EncryptionKey(BadsecretsBase):

    identify_regex = re.compile(r"^(?:[A-Za-z0-9+\/=%]+)$")

    @classmethod
    def password_derive_key(self, password, salt, length, count):
        return KDF.PBKDF1(password, salt, length, count=100)

    def prepare_keylist(self, include_machinekeys=False):

        if include_machinekeys:
            for l in self.load_resource("aspnet_machinekeys.txt"):
                try:
                    vkey, ekey = l.rstrip().split(",")
                    yield ekey
                except ValueError:
                    continue
        for l in self.load_resource("telerik_encryption_keys.txt"):
            ekey = l.strip()
            yield ekey

    def telerik_derivekeys(self, ekey, key_derive_mode):
        if key_derive_mode == "PBKDF1_MS":
            return self.telerik_derivekeys_PBKDF1_MS(ekey)
        elif key_derive_mode == "PBKDF2":
            return self.telerik_derivekeys_PBKDF2(ekey)
        else:
            raise Telerik_EncryptionKey_Exception("Invalid key_derive_mode")

    def telerik_derivekeys_PBKDF1_MS(self, ekey):
        csharp_pbkdf1 = Csharp_pbkdf1(ekey.encode(), bytes(telerik_hardcoded_salt), 100)
        derivedKey = csharp_pbkdf1.GetBytes(32)
        derivedIV = csharp_pbkdf1.GetBytes(16)
        return derivedKey, derivedIV

    def telerik_derivekeys_PBKDF2(self, ekey):
        pbkdf1 = KDF.PBKDF2(ekey.encode(), bytes(telerik_hardcoded_salt), dkLen=48)
        derivedKey = pbkdf1[:32]
        derivedIV = pbkdf1[32:]
        return derivedKey, derivedIV

    @classmethod
    def telerik_encrypt(self, derivedKey, derivedIV, dialog_parameters_pt):

        cipher = AES.new(derivedKey, AES.MODE_CBC, derivedIV)
        dialog_parameters_b64 = base64.b64encode(dialog_parameters_pt.encode()).decode().encode("utf-16le")
        dialog_parameters_raw = pad(dialog_parameters_b64, AES.block_size)
        encrypted_bytes = cipher.encrypt(dialog_parameters_raw)
        return base64.b64encode(encrypted_bytes).decode()

    @classmethod
    def telerik_decrypt(self, derivedKey, derivedIV, dp_enc):
        if not len(dp_enc) > 0:
            return None

        cipher = AES.new(derivedKey, AES.MODE_CBC, derivedIV)
        try:
            pt_raw = cipher.decrypt(dp_enc)
        except ValueError:
            return None
        original_bytes = unpad(pt_raw)
        try:
            decoded_bytes = original_bytes.decode("utf-16le")
        except UnicodeDecodeError:
            return None
        dialog_parameters = base64.b64decode(decoded_bytes).decode()
        return dialog_parameters

    def check_secret(self, dialogParameters_raw, key_derive_mode="PBKDF1_MS"):
        if not self.identify(dialogParameters_raw):
            return None

        dialogParametersB64 = urllib.parse.unquote(dialogParameters_raw)
        dp_enc = base64.b64decode(dialogParametersB64[:-44])
        for ekey in self.prepare_keylist():
            derivedKey, derivedIV = self.telerik_derivekeys(ekey, key_derive_mode)
            dialog_parameters = self.telerik_decrypt(derivedKey, derivedIV, dp_enc)
            if not dialog_parameters:
                continue
            if dialog_parameters.isascii():
                return {
                    "Telerik.Web.UI.DialogParametersEncryptionKey": ekey,
                    "DialogParameters": dialog_parameters,
                }
        return None

    def encryptionkey_probe_generator(self, hash_key, key_derive_mode, include_machinekeys=True):
        test_string = b"AAAAAAAAAAAAAAAAAAAA"
        dp_enc = base64.b64encode(test_string).decode()

        for ekey in self.prepare_keylist(include_machinekeys=include_machinekeys):
            derivedKey, derivedIV = self.telerik_derivekeys(ekey, key_derive_mode)
            ct = self.telerik_encrypt(derivedKey, derivedIV, dp_enc)
            h = hmac.new(hash_key.encode(), ct.encode(), self.hash_algs["SHA256"])
            yield (f"{ct}{base64.b64encode(h.digest()).decode()}", ekey)
