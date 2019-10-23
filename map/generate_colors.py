import seaborn as sns

def generate_colors(n):
  rgb_values = sns.color_palette("husl", n)
  hex_values = rgb_values.as_hex()
  return hex_values