import pytest
import variable_integer

@pytest.mark.parametrize("integer,representation", (
  (0, (0x00,)),
  (127, (0x7f,)),
  (128, (0x80, 0x01)),
  (16_383, (0xFF, 0x7F)),
  (16_384, (0x80, 0x80, 0x01) ),
  (2_097_151, (0xFF, 0xFF, 0x7F)),
  (2_097_152, (0x80, 0x80, 0x80, 0x01)),
  (268_435_455, (0xFF, 0xFF, 0xFF, 0x7F)),
))
def test_variable_integer(integer: int, representation: tuple):
  assert variable_integer.var_int(integer) == representation