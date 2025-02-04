from application.user.password import PasswordValidator, get_password_hash, verify_password


class TestPassword:
    def test_get_password_hash(self, password):
        hash_password = get_password_hash(password)
        assert password != hash_password

    def test_verify_password_success(self, password):
        hash_password = get_password_hash(password)
        is_correct = verify_password(password, hash_password)
        assert is_correct

    def test_verify_password_unsuccess(self, password):
        wrong_password = "1234"
        hash_password = get_password_hash(password)
        is_correct = verify_password(wrong_password, hash_password)
        assert not is_correct


class TestPasswordValidator:
    good_password = "Ab12345@"

    def test_validate_password_success(self):
        validator = PasswordValidator(self.good_password)
        errors = validator.validate_password()
        assert not errors

    def test_validate_password_errors(self):
        bad_password = "!"
        validator = PasswordValidator(bad_password)
        errors = validator.validate_password()
        expected_errors = {
            validator.short_password_msg,
            validator.upper_letter_msg,
            validator.lower_letter_msg,
            validator.digit_msg,
            validator.symbol_msg,
        }
        assert expected_errors == set(errors)

    def test__check_length_success(self):
        validator = PasswordValidator(self.good_password)
        validator._check_length()
        assert not validator._errors

    def test__check_length_error(self):
        password = "Ab1234@"
        validator = PasswordValidator(password)
        validator._check_length()
        assert validator.short_password_msg in validator._errors

    def test__check_upper_letter_success(self):
        validator = PasswordValidator(self.good_password)
        validator._check_upper_letter()
        assert not validator._errors

    def test__check_upper_letter_error(self):
        password = "ab1234@"
        validator = PasswordValidator(password)
        validator._check_upper_letter()
        assert validator.upper_letter_msg in validator._errors

    def test__check_lower_letter_success(self):
        validator = PasswordValidator(self.good_password)
        validator._check_lower_letter()
        assert not validator._errors

    def test__check_lower_letter_error(self):
        password = "AB1234@"
        validator = PasswordValidator(password)
        validator._check_lower_letter()
        assert validator.lower_letter_msg in validator._errors

    def test__check_digit_success(self):
        validator = PasswordValidator(self.good_password)
        validator._check_digit()
        assert not validator._errors

    def test__check_digit_error(self):
        password = "AbCdeF@@"
        validator = PasswordValidator(password)
        validator._check_digit()
        assert validator.digit_msg in validator._errors

    def test__check_symbol_success(self):
        validator = PasswordValidator(self.good_password)
        validator._check_symbol()
        assert not validator._errors

    def test__check_symbol_error(self):
        password = "Ab123456"
        validator = PasswordValidator(password)
        validator._check_symbol()
        assert validator.symbol_msg in validator._errors

    def test__check_symbol_unknown(self):
        password = "Ab12345("
        validator = PasswordValidator(password)
        validator._check_symbol()
        assert validator.symbol_msg in validator._errors
