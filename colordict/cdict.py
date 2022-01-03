"""Module containing the main class of the colordict package: ColorDict."""

import json
import os
import typing
import colordict.color
from collections.abc import Sequence

_package_path = os.path.dirname(__file__)


class ColorDict:
	"""Class that holds colors extracted from palettes.

	Args:
		palettes: List of palettes located in the ``palettes_path`` directory that should be
			loaded by this ColorDict instance. By default, loads all palettes.
		palettes_path: Path from which the palettes specified in the ``palettes`` parameter will
			be loaded. Defaults to ".../colordict/palettes".
		color_space: Which color class should be used to load the colors. Any of the defined
			:doc:`color classes <color>` can be used.
		**kwargs: Any other keyword argument specified in this constructor will be passed on to
			the constructor of the color class identified in the color_space parameter.

	Examples:
		.. code-block:: python

			c = ColorDict(color_space=sRGBColor, norm=1)

		Will create a ``ColorDict`` where all color entries are ``sRGBColor`` objects that have
		their norm attribute set to 1.

	Attributes:
		colors: A list of all colors currently loaded in the ``ColorDict``.
		palettes: A dictionary containing all palettes currently loaded in the ``ColorDict``.
			The palettes are keys in the dictionary which map to a list of color names.
		color_space: Stores the value passed to the constructor in the ``color_space`` parameter.
			**This property is read-only and can't be set outside the ColorDict constructor.**
		palettes_path: Stores the value passed to the constructor in the ``palettes_path``
			parameter.
	"""

	def __init__(self,
	             palettes: list = None,
	             palettes_path: str = "",
	             color_space: typing.Type[colordict.color.ColorBase] = colordict.color.sRGBColor,
	             **kwargs):
		self._color_space = color_space
		self.palettes_path = palettes_path if palettes_path else os.path.join(_package_path, 'palettes')
		self._changed = set()
		self._kwargs = kwargs
		self.colors = set()
		self.palettes = {}
		for palette in os.scandir(self.palettes_path):
			pal_name = palette.name[:palette.name.index('.')]
			if palettes is None or pal_name in palettes:
				with open(palette.path, 'r') as file:
					pal_dict = json.load(file)
				if pal_dict:
					self.palettes[pal_name] = list(pal_dict)
					for name, value in pal_dict.items():
						setattr(self, name, self.color_space._from_rgba(value, **kwargs))
						self.colors.add(name)

	@property
	def color_space(self):
		return self._color_space

	def get_color(self, color_name) -> colordict.color.ColorBase:
		return getattr(self, color_name)

	def named(self, color: Sequence) -> list:
		color_list = []
		for name in self.colors:
			if self.get_color(name) == color: color_list.append(name)
		return color_list

	def add(self, name: str, color: Sequence, palette='independent', check=True):
		forbidden = (
			"color_space",
			"palettes_path",
			"_changed",
			"_kwargs",
			"colors",
			"palettes"
		)
		if name in forbidden:
			raise ValueError(f"'{name}' is a reserved attribute name of ColorDict")
		elif check and hasattr(self, name):
			raise ValueError(f'Key "{name}" was not added because it already exists with value {self.get_color(name)}')
		setattr(self, name, self._interpret_color_input(color))
		self.colors.add(name)
		if palette not in self.palettes: self.palettes[palette] = []
		self.palettes[palette].append(name)
		self._changed.add(palette)

	def update(self, name, color):
		setattr(self, name, self._interpret_color_input(color))
		for palette in self.palettes:
			if name in palette:
				self._changed.add(palette)

	def remove(self, name, palette):
		self.palettes[palette].remove(name)
		self._changed.add(palette)

	def remove_all(self, name):
		delattr(self, name)
		for palette, pal_list in self.palettes.items():
			self._changed.add(palette)
			try:
				pal_list.remove(name)
			except ValueError:
				pass

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
					self.add(name, value, palette, False)

	def _interpret_color_input(self, color: Sequence):
		"""Tries to interpret user input and build a color to be used in the context of this
		ColorDict instance."""
		if isinstance(color, colordict.color.ColorBase):
			return self.color_space._from_rgba(color._rgba, **self._kwargs)
		# Color spaces that accept a single mandatory parameter for construction
		elif self.color_space in (colordict.color.HexColor,):
			return self.color_space(color, **self._kwargs)
		# Assume that the color space accepts multiple unnamed mandatory parameters for construction
		return self.color_space(*color, **self._kwargs)
	# If a color space that accepts only keyword arguments is latter created, its logic can also
	# be incorporated here
