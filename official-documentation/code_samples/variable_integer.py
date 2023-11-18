def var_int(number: int) -> tuple:
  # This 2 lines does not show in the original psuodo code.
  if number == 0:
    return (0,)
  _n = number
  bytes_repr = []
  while _n > 0:
    encoded_byte = _n % 128
    _n //= 128
    if _n > 0:
      encoded_byte |= 128
    bytes_repr.append(encoded_byte)
  return tuple(bytes_repr)

  
if __name__ == "__main__":
  print(var_int(16_384))