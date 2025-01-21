from application.user.password import get_password_hash, verify_password


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
