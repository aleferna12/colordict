colordict

A package to allow for easy maintenance of a color dictionary with palettes, so you can use the colors that you like in 
your different projects.

The aim of this project was to create a simple library to manage color names and color values. There are some colors which 
are so commonly used that the need to manually copy rgb or hex values becomes a burden. That's where ColorDict comes in,
 as it allows for much easier organizing of your prefered colors in a simple dictionary!

Another feature of this package is the LinearGrad, which is used to work with transition of colors in a gradient.

Quick example on how to use the library (more examples in the "Examples of usage" section):

    from colordict import *
    
    colors = ColorDict()
    red = colors['red']
    red_hex_string = colors['red', 'hex']
    rainbow_colors = colors.palettes['rainbow']
    
    rainbow_gradient = LinearGrad([colors[color] for color in rainbow_colors])

# To install:

Run:

    python -m pip install colordict

# Using ColorDict:

The ColorDict class is the main feature of this package. It is used to organize your colors in an easy and intuitive way.
All colors are saved as a json dictionary in the "palettes" directory of the package (or wherever you set to with the 
`palettes_path` parameter). When you create an instance of `ColorDict`, these colors are loaded as keys, and can be accessed
just as any python dictionary. Because of this, **there can be only one color value per key name**, and disrespecting 
this rule will lead to inconsistancies. Note, however, that **multiple keys can map to the same value**.

- Is fine:

        value = (255, 0, 0)
        colordict_instance.add('red', value)
        colordict_instance.add('carmesim', value)
        
- Is dangerous:

        name = 'red'
        colordict_instance.add(name, (255, 0, 0))
        colordict_instance.add(name, (128, 0, 0))

> See the topic on adding and removing colors for more insight in how to properly add colors to the dictionary

## Initializing a ColorDict instance:
    
        colordict_instance = ColorDict(norm=255, mode='rgb', palettes_path="", is_grayscale=False, palettes='all')
        
    - `norm` represents the standart norm of the dictionary. Any value retrieved from a key will be normalized to that. 
    Any value set to a key should be in this norm
    - `mode` is the format in which values will be retrieved (see section on retrieving values for more on that)
    - `palettes_path` set the path from which the instance will load the palettes (and where they are going to be saved as well)
    - If `is_grayscale=True`, values retrieved from keys will all be converted to shades of gray
    - You can load only some palettes by passing a list of palettes to the `palettes` argument. `palettes=all`, the default, will load all palettes instead
    
- For example, running:

        norm_dict = ColorDict(norm=1)
        hex_dict = ColorDict(mode='hex')
        gray_dict = ColorDict(is_grayscale=True)
        fluo_dict = ColorDict(palettes=['fluorescent'])
        
        print(norm_dict['red'])
        print(hex_dict['red'])
        print(gray_dict['red'])
        print(fluo_dict['red'])
        
    Would print:
    
        (1.0, 0.0, 0.0)
        #ff0000
        (76.5, 76.5, 76.5)
        
    And a `KeyError` would be raised for `fluo_dict`, as `red` is not a color of the "fluorescent" palette
    
- `colordict_instance.palettes` is a dictionary containing every loaded palette and the name of the colors contained in each of them
- `colordict_instance.norm` represents the dictionary's current norm. It is read-only
- `colordict_instance.mode` represents the dictionary's current mode ( 'rgb', 'rgba', 'hex', 'hls', 'hsv' or 'yiq')
- `colordict_instance.is_grayscale` represents if the dictionary is grayscale or not
- `colordict_instance.palettes_path` represents the path to the directory where palettes are stored

### Retrieving color values from a ColorDictionary instance:

- Color values can be retrieved from a `ColorDict` by doing:

         colordict_instance['color_name']
         
- You can further specify a format in which the value will be returned by doing:

        colordict_instance['color_name', 'mode']
         
    - Example:
    
            colordict_instance['red', 'hex']
            
        Would return: `"#ff0000"`
        
- As of right now, 'rgb', 'rgba', 'hex', 'hls', 'hsv' and 'yiq' modes are available
- If you don't specify a mode, the attribute `colordict_instance.mode` will be used instead
- You can also use default methods from dictionaries, such as `keys()`, `values()` and `items()`, but note that any
values returned by these methods will be in rgba format

### Adding, changing and removing colors:

- The add and remove methods are only intended to use when you want to add or remove colors to/from a specific palette or intend to save them permanently latter

        color_instance.add('color_name', rgb_a, palette='independent', check=True)
        color_instance.remove('color_name', palette)
        
    > Note that the method `remove()` will only remove the color from a particular palette. You can use the method `remove_all('color_name')` if you wish to remove a color from all palettes and delete the dictionary key
        
- If you only wish to locally add colors to a ColorDict but don't want the `save()` method to save them, you can simply do:

        colordict_instance['color_name'] = rgb_a
        
    > **Note that whenever adding values, the format must be (r, g, b) or (r, g, b, a)**
    
- If you want to change the color value associated with a particular color name, you can do:

        colordict_instance['color_name'] = new_rgb_a

    > Note, however, that this change will not be permanent

- If you want to permanently save the change to a color value, use:
    
        color_instance.add('color_name', rgb_a, 'palette', check=False)  
    >In this case you probably will want to `color_instance.save()` afterwards

- Example:

        # Adding color 'strawberry' with value (200, 63, 73) to palette 'fruits':
        color_instance.add('strawberry', (200, 63, 73), 'fruits')
        
        # Adding color 'mango' with value (255, 130, 67) locally:
        colordict_instance['mango'] = (255, 130, 67)
        
        # Changing the value of 'strawberry' to (255, 0, 0):
        colordict_instance['strawberry'] = (255, 0, 0)

        # Removing color 'lemon' from palette 'fruits':
        color_intance.remove('lemon', 'fruits')
        
        # Removing color 'orange' from all palettes:
        colordict_instance.remove_all('orange')
        
- If you don't provide a palette name when using `add()`, colors will be stored in a palette called "independent"
- Palettes are automatically created when adding colors to them if necessary
- By default, trying to add colors that already exists will not work and a message will be printed telling you so
    > This was made to prevent you from unwillingly overwriting colors that already exist
    - If you are sure you are not creating different colors with the same name (e.g. you are just creating a palette of existing colors), then set `check=False` when adding a color:
    
            colordict_instance.add('color_name', rgb_a, palette='my_palette', check=False)
            
### Saving, doing backups and restoring backups:

- If you want to save the current state of the ColorDict instance (this saves each palette individually as explained in the beginning of this section), you can simply do:

        colordict_instance.save()
        
- To create a backup of the current state of the `ColorDict` instance (in case you are afraid of messing things up), you can do:

        colordict_instance.backup()
        
- To restore the ColorDict instance with the existing backup, you do:

        colordict_instance.restore()
        
> Note that neither backup or restore functions automatically `save()`. If thats the intention, you must call it separately

## General functions:

There are a few useful functions available in this package:

### Conversion between color systems:

These functions return the color inputed as the output format.

- If you want to convert rgb to hex (rgb norm must be 255):

        rgb_to_hex(rgb)
        
- If you want to convert hex to rgb:

        hex_to_rgb('hex')
        
- You can also freely convert between 'rgb' and 'hls', 'hsv' or 'yiq' (norm of input must be 1):

        hls_to_rgb(hls)
        
- Example:

        # Converting red around
        rgb = hex_to_rgb('#ff0000')
        hls = rgb_to_hls(rgb)
        rgb2 = hls_to_rgb(hls)
        yiq = rgb_to_yiq(rgb2)
        print(yiq)
        
    Would print: `(76.5, 152.745, 54.315)`
        
### Other:

- If you want the gray equivalent of a color:

        grayscale(rgb)
        
- If you want to renorm a color value (let's say from (255, 255, 255) to (1, 1, 1)):

        renorm(rgb_a, old, new)
        
# Using gradients:

As of right now, the only available gradient is LinearGrad, which uses linear interpolation as the algorithm.

### LinearGrad

- To initialize a `LinearGrad` instance, you'll only need a set of rgb or rgb_a values:

        grad = LinearGrad(list_of_rgbs)
        
- You can then obtain the color in a certain percentage of the gradient by calling the instance itself with said percentage as an argument:

        color_at_percentage = grad(percentage)
        
- You can also obtain a list of n color values equally interspaced:

        color_list = grad.n_colors(n, stripped=True)
        
    - The returned list will never include the first and last color values of the list you used to create the `LinearGrad` instance, unless you set `stripped=False`, in which case they will always be present
        
- `grad.colors` represents the color values loaded in the gradient originally
        
- Example:
        
        # Creating a linear gradient between red, green and blue:
        grad = LinearGrad([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
        
        # Getting a shade of yellow between red and green:
        yellow = grad(0.33)
        
        # Getting 100 color values interspaced between all three colors:
        rgbs = grad.n_colors(100)

# Examples of usage

- Using tkinter to render a few rainbow-colored lines and a "aquamarine" rectangle on the screen:

        import tkinter as tk
        import colordict as cd

        colors = cd.ColorDict(mode='hex')
        master = tk.Tk()

        w = tk.Canvas(master, width=500, height=500)
        w.pack()

        # Referencing the "aquamarine" color from "colors"
        w.create_rectangle([10, 400, 50, 500], fill=colors['aquamarine'])
        # Doing the same recursevely for all color names in "colors.palettes['rainbow']"
        for i, color in enumerate(colors.palettes['rainbow']):
            w.create_line([0, 0, (i + 1) * 200, 500], fill=colors[color])

        tk.mainloop()

- Using tkinter to visualize a rainbow gradient and the colors composing it:

        import tkinter as tk
        import colordict as cd
        import my_tools as mt

        colors = cd.ColorDict()


        class Window(tk.Tk):
            def __init__(self):
                super().__init__()
                self.geometry('1200x400')
                self.resizable(False, False)

                self.canvas = tk.Canvas(width=1200, height=400)
                self.canvas.pack()
                
                # Creating a gradient that goes through all colors in the 'rainbow' palette
                palette = colors.palettes['rainbow']
                self.grad = cd.LinearGrad([colors[name] for name in palette])
                n = 1200
                # Creating a thin rectangle for every color value returned by the "n_colors()" method
                for i, color in enumerate(self.grad.n_colors(n)):
                    self.canvas.create_rectangle(
                        [i*1200/n, 0, (i + 1)*1200/n, 200],
                        fill=cd.rgb_hex(color),
                        outline=''
                    )
                # Creating a rectangle for every color in the 'rainbow' palette
                for i, color in enumerate(palette):
                    self.canvas.create_rectangle(
                        [i*1200/len(palette), 200, (i + 1)*1200/len(palette), 400],
                        fill=colors[color, 'hex'],
                        outline=''
                    )


        win = Window()
        win.mainloop()
        
- Simple color-picker using tkinter and sorting values by their hue:

        import tkinter as tk
        import colordict as cd
        from functools import partial
        
        # Creating the dictionary instance
        colors = cd.ColorDict(mode='hex', norm=1)
        
        
        def colorname(instance, name, val):
            global switch
        
            if switch: widget = instance.text2
            else: widget = instance.text1
            widget.config(bg=val)
            widget.delete('1.0', tk.END)
            # Converting to various formats and displaying them
            widget.insert('1.0', f'{name}\nRGBA: {cd.hex_to_rgb(val)}\nHEX: {val}\nPALETTES:'
                                 f'{[pal_name for pal_name, pal_list in colors.palettes.items() if name in pal_list]}')
            if sum(cd.hex_to_rgb(val))/3 < 80:
                widget.config(foreground=colors['white'])
            else:
                widget.config(foreground=colors['black'])
        
            switch = not switch
        
        
        class Window(tk.Tk):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.title('Color Picker')
                self.geometry('1152x768')
                self.resizable(0, 0)
                self.update_idletasks()
        
                self.colors_btns = {}
                self.size = self.winfo_height()/(int(len(colors)**0.5) + 1)
                row = 0
                col = 0
                # Creating a list of ordered hue values and color names
                hues = []
                for name in colors:
                    hls = colors[name, 'hls']
                    hues.append((hls[0], name))
                hues.sort()
                for _, color in hues:
                    f = tk.Frame(self, height=self.size, width=self.size)
                    f.pack_propagate(0)
                    f.grid(row=row, column=col)
                    self.colors_btns[color] = tk.Button(
                        f, bg=colors[color], command=partial(colorname, self, color, colors[color])
                    )
                    self.colors_btns[color].pack(fill=tk.BOTH, expand=1)
                    if (col + 1) * self.size < self.winfo_height(): col += 1
                    else:
                        col = 0
                        row += 1
        
                comp_size = self.winfo_width() - self.winfo_height()
                self.frame1 = tk.Frame(self, height=comp_size, width=comp_size)
                self.frame1.pack_propagate(0)
                self.frame1.place(x=self.winfo_height(), y=0)
                self.frame2 = tk.Frame(self, height=comp_size, width=comp_size)
                self.frame2.pack_propagate(0)
                self.frame2.place(x=self.winfo_height(), y=comp_size)
                self.text1 = tk.Text(self.frame1, font=("Helvetica", 12), bd=0)
                self.text1.pack(fill=tk.BOTH, expand=1)
                self.text2 = tk.Text(self.frame2, font=("Helvetica", 12), bd=0)
                self.text2.pack(fill=tk.BOTH, expand=1)
        
        
        win = Window()
        
        switch = 0
        
        win.mainloop()
