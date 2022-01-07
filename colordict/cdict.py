"""Module containing the main class of the colordict package: ``ColorDict``."""

import json
import os
import typing
import logging
from colordict.color import *
from collections.abc import Sequence

_package_path = os.path.dirname(__file__)


class ColorDict:
	"""Class that holds colors extracted from palettes.

	Args:
		palettes: List of palettes located in the ``palettes_path`` directory that should be
			loaded by this ``ColorDict`` instance. By default, loads all palettes.
		palettes_path: Path from which the palettes specified in the ``palettes`` parameter will
			be loaded. Defaults to ".../colordict/palettes".
		color_space: Which color class should be used to load the colors. Any of the defined
			:doc:`color classes <color>` can be used.
		**kwargs: Any other keyword argument specified in this constructor will be passed on to
			the constructor of the color class identified in the color_space parameter.

	Examples:
		.. code-block:: python

			cdict = ColorDict(color_space=sRGBColor, norm=1)

		Will create a ``ColorDict`` where all color entries are ``sRGBColor`` objects that have
		their norm attribute set to 1.

	Attributes:
		colors: A list of all colors currently loaded in the ``ColorDict``.
		palettes: A dictionary containing all palettes currently loaded in the ``ColorDict``.
			The palettes are keys in the dictionary which map to a list of color names.
		color_space: Stores the value passed to the constructor in the ``color_space`` parameter.
			**This property is read-only and can't be set outside the ``ColorDict`` constructor.**
		palettes_path: Stores the value passed to the constructor in the ``palettes_path``
			parameter.
	"""

	def __init__(self,
	             palettes: list = None,
	             palettes_path: str = "",
	             color_space: typing.Type[ColorBase] = sRGBColor,
	             **kwargs):
		self._color_space = color_space
		self.palettes_path = palettes_path if palettes_path else os.path.join(_package_path, 'palettes')
		self._changed = set()
		self._kwargs = kwargs
		self.colors = set()

		self.palettes = {}
		for palette in os.scandir(self.palettes_path):
			pal_name = palette.name.replace(".json", "")
			if palettes is None or pal_name in palettes:
				with open(palette.path, 'r') as file:
					pal_dict = json.load(file)
				self.palettes[pal_name] = list(pal_dict)
				for name, value in pal_dict.items():
					value = tuple(value)
					existing = self.get_color(name)
					# Color didn't exist in dictionary and everything is alright
					if existing is None:
						setattr(self, name, self.color_space._from_rgba(value, **kwargs))
						self.colors.add(name)
					# Color already existed with a different rgba, which means problems
					elif getattr(existing, "_rgba", None) != value:
						logging.warning(f"Duplicated key with name '{name}' and rgba '{value}' already exists with "
						                f"rgba '{getattr(existing, '_rgba', None)}'. Please remove one of the "
						                f"occurrences of '{name}' with the 'remove' method to avoid unexpected "
						                f"results.")

	@property
	def color_space(self):
		return self._color_space

	def get_color(self, name: str, default=None) -> ColorBase:
		"""Retrieves a color from the ``ColorDict`` given its name.

		This is a noob-friendly wrapper for ``getattr()``.

		Args:
		    default: What will be returned in the case that ``name`` is not found in the ``ColorDict``.
			name: Name of the color you want to get.

		Examples:
			>>> cdict = ColorDict(color_space=sRGBColor)
			>>> cdict.get_color("red") # Same as 'cdict.red'
			sRGBColor(255.0, 0.0, 0.0)
		"""
		return getattr(self, name, default)

	def names(self, color: Sequence) -> list:
		"""Finds the names of the provided color in this ``ColorDict``.

		Compares the provided ``color`` to every color the ``ColorDict`` contains and returns the
		names of the colors that are equivalent to the one provided.

		Args:
			color: The value of the color you want to search for. If you want to be *absolutely*
				sure to find every entry in the ``ColorDict`` based on this parameter, you should
				provide the color in the form of a :doc:`color class <color>`. Alternatively,
				any color-like object can be provided and the method will try its best to return
				accurate results (it mostly does).

		Examples:
			>>> cdict = ColorDict(color_space=sRGBColor)
			>>> cdict.names(HexColor("#ff0000")) # Works because HexColor("#ff0000") == sRGBColor(255.0, 0.0, 0.0)
			['red']
			>>> cdict.names((255, 0, 0)) # Also works because (255, 0, 0) == sRGBColor(255.0, 0.0, 0.0)
			['red']
			>>> cdict.names("#ff0000") # Doesn't work because "#ff0000" != sRGBColor(255.0, 0.0, 0.0)
			[]
			>>> hex_cdict = ColorDict(color_space=HexColor)
			>>> hex_cdict.names("#ff0000") # Now it works because "#ff0000" == HexColor("#ff0000")
			['red']

			.. note::

				Be careful when searching for colors that have been created with the ``round_to``
				flag, since :code:`sRGBColor(33, 33, 33) != sRGBColor(33.333, 33.333, 33.333, round_to=0)`,
				for example.
		"""
		color_list = []
		for name in self.colors:
			if self.get_color(name) == color: color_list.append(name)
		return color_list

	def add(self, name: str, color: Sequence, palette='unassigned'):
		"""Adds a color to a palette.

		.. warning::

			Two colors with the same name but different values are invalid and can not coexist in a
			same ``ColorDict``. You should therefore avoid reusing names for already existing colors
			at all costs. If you are unsure if a color name is already taken for another color, try:

			.. code-block :: python

				test_cdict = ColorDict(palettes=None)
				print(test_cdict.get_color(name) == color)

			If the print statement prints ``False``, you can be sure your ``name`` is valid.

		Args:
			name: Name to be assigned to the new color.
			color: The value of the color to be created. Can be an instance of any
				:doc:`color class <color>` or, alternatively, a color-like object that resembles
				the color you want to add.
			palette: Palette in which the new color will be added. Defaults to a palette called
				"unassigned".

		Examples:
			Creating a new gray color and adding it to the default palette:

			>>> cdict = ColorDict()
			>>> cdict.add("gray_96", (96, 96, 96))
			>>> cdict.gray_96
			sRGBColor(96, 96, 96)

			Adding an already existing color to another palette:

			>>> cdict.add("red", cdict.get_color("red"), "palette_for_my_project")

			Trying to assign a different value to the already existing ``red`` color results in an
			exception:

			>>> cdict.add("red", (0, 255, 255))
			ValueError: key 'red' with rgba '(0, 1, 1, 1)' can't be created because it already
			exists with rgba '(1, 0, 0, 1)'

		"""
		attributes = [
			"_color_space",
			"palettes_path",
			"_changed",
			"_kwargs",
			"colors",
			"palettes"
		]
		# Tests to detect invalid color names
		if name in attributes + dir(ColorDict):
			raise ValueError(f"'{name}' is a reserved attribute name of ColorDict")
		color = self._interpret_color_input(color)
		existing = self.get_color(name)
		if existing is not None and getattr(existing, "_rgba", None) != color._rgba:
			raise ValueError(f"key '{name}' with rgba '{color._rgba}' can't be created because it already "
			                 f"exists with rgba '{getattr(existing, '_rgba', None)}'")

		setattr(self, name, color)
		self.colors.add(name)
		if palette not in self.palettes: self.palettes[palette] = []
		self.palettes[palette].append(name)
		self._changed.add(palette)

	def update(self, name: str, color: Sequence):
		"""Updates a color to a new value.

		Args:
			name: Name of the color to be updated.
			color: The value of the color to be updated. Can be an instance of any
				:doc:`color class <color>` or, alternatively, a color-like object that resembles
				the format of the color you want to update.

		"""

		if name in self.colors:
			setattr(self, name, self._interpret_color_input(color))
			for palette in self.palettes:
				if name in self.palettes[palette]:
					self._changed.add(palette)
		else:
			raise ValueError(f"Provided 'name' parameter is not a color loaded in this 'ColorDict'")

	def remove(self, name, palette):
		self.palettes[palette].remove(name)
		self.colors.remove(name)
		self._changed.add(palette)

	def remove_all(self, name):
		self.colors.remove(name)
		delattr(self, name)
		for palette in self.palettes:
			if name in self.palettes[palette]:
				self.palettes[palette].remove(name)
				self._changed.add(palette)

	def save(self):
		for palette in self._changed:
			pal_dict = {}
			for name in self.palettes[palette]:
				color = self.get_color(name)
				pal_dict[name] = color._rgba
			with open(os.path.join(self.palettes_path, palette + '.json'), 'w') as file:
				json.dump(pal_dict, file, indent=4)
		self._changed.clear()

	def backup(self):
		color_dict = {}
		for palette, color_list in self.palettes.items():
			color_dict[palette] = {}
			for name in color_list:
				color = self.get_color(name)
				color_dict[palette][name] = color._rgba
		with open(os.path.join(_package_path, 'backup.json'), 'w') as file:
			json.dump(color_dict, file, indent=4)

	def restore_backup(self):
		for name in self.colors:
			delattr(self, name)
		self.palettes.clear()
		self._changed.clear()
		with open(os.path.join(_package_path, 'backup.json'), 'r') as file:
			color_dict = json.load(file)
		for palette, color_list in color_dict.items():
			if color_list:
				for name, value in color_list.items():
					self.add(name, value, palette)

	def _interpret_color_input(self, color: Sequence) -> ColorBase:
		"""Tries to interpret user input and build a color to be used in the context of this
		``ColorDict`` instance."""
		if isinstance(color, ColorBase):
			return self.color_space._from_rgba(color._rgba, **self._kwargs)
		try:
			# Color spaces that accept a single mandatory parameter for construction
			if self.color_space in (HexColor,):
				return self.color_space(color, **self._kwargs)
			# Assume that the color space accepts multiple unnamed mandatory parameters for construction
			return self.color_space(*color, **self._kwargs)
		except:
			raise ValueError(f"An error has happened while trying to interpret '{color}' as a '{self.color_space}'."
			                 "Using colors defined in the 'color' submodule as a parameter instead may help")
