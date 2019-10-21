import random
import seaborn as sns

# def generate_colors(n):
#   rgb_values = []
#   hex_values = []
#   r = 254 #int(random.random() * 256)
#   g = 192 #int(random.random() * 256)
#   b = 54 #int(random.random() * 256)
#   step = 256 / n
#   for _ in range(n):
#     r += step
#     g += step
#     b += step
#     r = int(r) % 256
#     g = int(g) % 256
#     b = int(b) % 256
#     r_hex = hex(r)[2:]
#     g_hex = hex(g)[2:]
#     b_hex = hex(b)[2:]
#     hex_values.append('#' + r_hex + g_hex + b_hex)
#     rgb_values.append((r,g,b))
#   return hex_values

def generate_colors(n):
  rgb_values = sns.color_palette(None, n)
  hex_values = rgb_values.as_hex()
  return hex_values

