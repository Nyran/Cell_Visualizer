import csv, re, sys, colorsys

#empty dictionary
children_cell_dictionary = {}
combined_children_key = "combined_children"

min_color = [0,120,0]
max_color = [0,0,255]


def rgb_heat_map_color_for(value):
  h = ((1.0 - value) * 240) / 360

  #rgb_heat_map_values = colorsys.hls_to_rgb(h/float(360.0), 1.0, 0.5)
  rgb_heat_map_values = colorsys.hls_to_rgb(h, 0.5, 1.0)
  rgb_vals = [0.0, 0.0, 0.0]
  rgb_vals[0] = rgb_heat_map_values[0] * 255
  rgb_vals[1] = rgb_heat_map_values[1] * 255
  rgb_vals[2] = rgb_heat_map_values[2] * 255

  return rgb_vals


def create_combined_children_entry():
  if combined_children_key not in children_cell_dictionary:
    children_cell_dictionary[combined_children_key] = {}

def check_and_insert_child_idx(child_idx):
  if child_idx not in children_cell_dictionary:
    children_cell_dictionary[child_idx] = {}

def check_and_insert_cell_idx(child_idx, cell_idx):
  if cell_idx not in children_cell_dictionary[child_idx]:
    children_cell_dictionary[child_idx][cell_idx] = 1
  else:
    children_cell_dictionary[child_idx][cell_idx] += 1

def insert_cell_entry(child_idx, cell_idx):
  create_combined_children_entry()
  check_and_insert_child_idx(child_idx)
  check_and_insert_cell_idx(child_idx, cell_idx)
  check_and_insert_cell_idx(combined_children_key, cell_idx)

def load_cell_file(file_path):
  with open(file_path) as cell_file:
    for current_line in cell_file:
      current_line = re.sub("-","",current_line)
      current_line = re.sub("\r\n","",current_line)
      result_list = current_line.split(";")

      cell_id = result_list[1]
      cell_id_length = len(cell_id)
      if cell_id_length > 0:
        child_id = result_list[0]
        insert_cell_entry(child_id, cell_id)

def reparse_and_save_svg(file_path):

  for child_idx in children_cell_dictionary:

    child_one_dictionary = children_cell_dictionary[child_idx]

    min_value = 0
    max_value = 0

    currently_editing_cell = False
    current_cell_id = ""

    for cell_idx in child_one_dictionary:
      cell_idx_val = child_one_dictionary[cell_idx]
      if cell_idx_val > max_value:
        max_value = cell_idx_val

    output_file = open(file_path+".out."+child_idx, "w")

    with open(file_path) as svg_file:
      for current_line in svg_file:
        if currently_editing_cell == False:
          if "id=\"cell" in current_line:
            currently_editing_cell = True
            cell_id_uncleaned = current_line.split("cell",1)[1]
          
            #remove trailing quotation marks and newline character for lookup
            current_cell_id = str(re.sub("\"\n","",cell_id_uncleaned))

        else:
          if "fill:#" in current_line:
            currently_editing_cell = False;

            looked_up_value = 0


            if current_cell_id in child_one_dictionary:
              looked_up_value = child_one_dictionary[current_cell_id]

            enumerator = looked_up_value - min_value
            denominator = max_value - min_value
            
            interpolation_coefficient = enumerator / float(denominator)

            ###################### USE THIS BLOCK FOR 2 COLOR HEATMAP  --- START
            interpolated_red    = int(min_color[0] * (1.0 - interpolation_coefficient) + max_color[0] * (interpolation_coefficient) )
            interpolated_green  = int(min_color[1] * (1.0 - interpolation_coefficient) + max_color[1] * (interpolation_coefficient) )
            interpolated_blue   = int(min_color[2] * (1.0 - interpolation_coefficient) + max_color[2] * (interpolation_coefficient) )
            ###################### USE THIS BLOCK FOR 2 COLOR HEATMAP  --- END
            
            ###################### USE THIS BLOCK FOR RAINBOW HEATMAP  --- START
            vals = rgb_heat_map_color_for(interpolation_coefficient)

            interpolated_red = vals[0]
            interpolated_green = vals[1]
            interpolated_blue = vals[2]

            hex_val = ("%02x%02x%02x" % (interpolated_red, interpolated_green, interpolated_blue))
            ###################### USE THIS BLOCK FOR RAINBOW HEATMAP --- END

            current_line = re.sub(r"fill:#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})", "fill:#"+hex_val, current_line)

        output_file.write(current_line)
          

#put your custom cell data here
load_cell_file("zellen.csv")

#put your custom svg files with labeled cell inkscape objects here 
reparse_and_save_svg("plain_gaensemaennchen_map.svg")

