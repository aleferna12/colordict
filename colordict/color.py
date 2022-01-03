"""Module containing color classes that allow for easy conversion between color spaces.

This module contains different classes that represent a few of the most common `color spaces`_.

Although these classes may be used individually, they were originally designed to be used within
a :doc:`ColorDict <cdict>` object.

.. _color spaces: https://en.wikipedia.org/wiki/Color_model
"""
import colorsys
import abc


class ColorBase(metaclass=abc.ABCMeta):
	"""Base class from which all color classes inherit.

	.. note::

		This class is abstract and should not be instanciated.
	"""

	@abc.abstractmethod
	def __new__(cls, rgba: tuple, **kwargs):
		obj = super().__new__(cls)
		obj._rgba = tuple(rgba)
		return obj

	def __eq__(self, other):
		return self._rgba == other._rgba if isinstance(other, ColorBase) else False

	@classmethod
	@abc.abstractmethod
	def _from_rgba(cls, rgba, **kwargs):
		# Factory method to be called when reading the palette files
		pass

	def hex(self, **kwargs) -> "HexColor":
		"""Converts the current color to a hexadecimal representation.

		Args:
			**kwargs: Keyword arguments wrapped in this function will be passed on to the
				``HexColor`` constructor.
		"""
		return HexColor._from_rgba(self._rgba, **kwargs)

	def rgb(self, **kwargs) -> "sRGBColor":
		"""Converts the current color to an sRGB representation.

		Args:
			**kwargs: Keyword arguments wrapped in this function will be passed on to the
				``sRGBColor`` constructor.
		"""
		return sRGBColor._from_rgba(self._rgba, **kwargs)

	def hsl(self, **kwargs) -> "HSLColor":
		"""Converts the current color to an HSL representation.

		Args:
			**kwargs: Keyword arguments wrapped in this function will be passed on to the
				``HSLColor`` constructor.
		"""
		return HSLColor._from_rgba(self._rgba, **kwargs)

	def hsv(self, **kwargs) -> "HSVColor":
		"""Converts the current color to an HSV representation.

		Args:
			**kwargs: Keyword arguments wrapped in this function will be passed on to the
				``HSVColor`` constructor.
		"""
		return HSVColor._from_rgba(self._rgba, **kwargs)

	def cmyk(self, **kwargs) -> "CMYKColor":
		"""Converts the current color to a CMYK representation.

		Args:
			**kwargs: Keyword arguments wrapped in this function will be passed on to the
				``CMYKColor`` constructor.
		"""
		return CMYKColor._from_rgba(self._rgba, **kwargs)

	def cmy(self, **kwargs) -> "CMYColor":
		"""Converts the current color to a CMY representation.

		Args:
			**kwargs: Keyword arguments wrapped in this function will be passed on to the
				``CMYColor`` constructor.
		"""
		return CMYColor._from_rgba(self._rgba, **kwargs)


class ColorTupleBase(ColorBase, tuple, metaclass=abc.ABCMeta):
	"""Base class from which all color classes that are represented by tuples inherit.

	.. note::

		This class is abstract and should not be instanciated.
	"""

	@abc.abstractmethod
	def __new__(cls, iterable, rgba, include_a=False, round_to=-1):
		if not include_a:
			iterable = iterable[:-1]
		if round_to == 0:
			iterable = [round(val) for val in iterable]
		elif round_to > 0:
			iterable = [round(val, round_to) for val in iterable]
		obj = tuple.__new__(cls, iterable)
		obj._rgba = tuple(rgba)
		obj.include_a = include_a
		obj.round_to = round_to

		return obj

	def __repr__(self):
		return f"{self.__class__.__name__}{tuple.__repr__(self)}"

	def __eq__(self, other):
		return ColorBase.__eq__(self, other) if isinstance(other, ColorBase) else tuple.__eq__(self, other)


class sRGBColor(ColorTupleBase):
	"""Represents a color in the `RGB color space`_.

	.. _RGB color space: https://en.wikipedia.org/wiki/SRGB

	Args:
		r: Red component of the color.
		g: Green component of the color.
		b: Blue component of the color.
		a: Opacity component of the color. Defaults to ``None``, which means it will be the same
			as the ``norm`` parameter.
		norm: What the ``r``, ``g``, ``b``, and ``a`` components are normalized to (aka their highest
			possible value). Some common values for this parameter would be 255 or 1.
		include_a: Whether to include the opacity parameter ``a`` in the contructed tuple.
			Setting it to ``True`` may result in an object such as :code:`sRGBColor(255, 255, 0,
			255)` instead of :code:`sRGBColor(255, 255, 0)`, for exemple.
		round_to: Rounds the value of each color component to this many decimal places. Setting this
			parameter to 0 ensures that the components will be of type ``int``. The default, -1,
			means that the components won't be rounded at all.
	"""

	def __new__(cls, r: float, g: float, b: float, a: float = None, norm=255, include_a=False, round_to=-1):
		if a is None:
			a = norm

		if any(spec > norm for spec in (r, g, b, a)):
			raise ValueError(
				"'r', 'g', 'b' and 'a' parameters of sRGBColor can't be larger then the defined 'norm' parameter'")

		obj = super().__new__(cls,
		                      (r, g, b, a),
		                      (r / norm, g / norm, b / norm, a / norm),
		                      include_a=False,
		                      round_to=round_to)
		obj.norm = norm
		return obj

	def __init__(self, **kwargs):
		pass

	@classmethod
	def _from_rgba(cls, rgba, norm=255, include_a=False, round_to=-1):
		rgba_ = [spec * norm for spec in rgba]
		obj = super().__new__(cls,
		                      rgba_,
		                      rgba,
		                      include_a=include_a,
		                      round_to=round_to)
		obj.norm = norm
		return obj


class HSLColor(ColorTupleBase):
	"""Represents a color in the `HSL color space`_.

	.. _HSL color space: https://en.wikipedia.org/wiki/HSL_and_HSV

	Args:
		h: HUE component of the color.
		s: Saturation component of the color.
		l: Lightness component of the color.
		a: Opacity component of the color. Defaults to ``None``, which means it will be the same
			as the ``sla_norm`` parameter.
		h_norm: What the ``h`` component is normalized to (aka its highest possible
			value). Some common values for this parameter would be 360 or 1.
		sla_norm: What the ``s``, ``l`` and ``a`` components are normalized to (aka their highest
			possible value). Some common values for this parameter would be 1 or 100.
		include_a: Whether to include the opacity parameter ``a`` in the contructed tuple.
			Setting it to ``True`` may result in an object such as :code:`HSLColor(360, 1, 0,
			1)` instead of :code:`HSLColor(360, 1, 0)`, for exemple.
		round_to: Rounds the value of each color component to this many decimal places. Setting this
			parameter to 0 ensures that the components will be of type ``int``. The default, -1,
			means that the components won't be rounded at all.
	"""

	def __new__(cls, h: float, s: float, l: float, a: float = None, h_norm=360, sla_norm=1, include_a=False,
	            round_to=-1):
		if a is None:
			a = sla_norm

		if h > h_norm:
			raise ValueError("'h' parameter of HSLColor can't be larger then the defined 'h_norm' parameter'")
		if any(spec > sla_norm for spec in (s, l, a)):
			raise ValueError(
				"'s', 'l' and 'a' parameters of HSLColor can't be larger then the defined 'sla_norm' parameter'")

		rgba = colorsys.hls_to_rgb(h / h_norm, l / sla_norm, s / sla_norm) + (a / sla_norm,)
		obj = super().__new__(cls, (h, s, l, a), rgba, include_a=include_a, round_to=round_to)
		obj.h_norm = h_norm
		obj.sla_norm = sla_norm

		return obj

	def __init__(self, **kwargs):
		pass

	@classmethod
	def _from_rgba(cls, rgba, h_norm=360, sla_norm=1, include_a=False, round_to=-1):
		hls = colorsys.rgb_to_hls(*rgba[:-1])
		hsla = (hls[0] * h_norm, hls[2] * sla_norm, hls[1] * sla_norm, rgba[-1] * sla_norm)

		obj = super().__new__(cls,
		                      hsla,
		                      rgba,
		                      include_a=include_a,
		                      round_to=round_to)
		obj.h_norm = h_norm
		obj.sla_norm = sla_norm
		return obj


class HSVColor(ColorTupleBase):
	"""Represents a color in the `HSV color space`_.

	.. _HSV color space: https://en.wikipedia.org/wiki/HSL_and_HSV

	Args:
		h: HUE component of the color.
		s: Saturation component of the color.
		v: Value component of the color.
		a: Opacity component of the color. Defaults to ``None``, which means it will be the same
			as the ``sva_norm`` parameter.
		h_norm: What the ``h`` component is normalized to (aka its highest possible
			value). Some common values for this parameter would be 360 or 1.
		sva_norm: What the ``s``, ``v`` and ``a`` components are normalized to (aka their highest
			possible value). Some common values for this parameter would be 1 or 100.
		include_a: Whether to include the opacity parameter ``a`` in the contructed tuple.
			Setting it to ``True`` may result in an object such as :code:`HSVColor(360, 1, 0,
			1)` instead of :code:`HSVColor(360, 1, 0)`, for exemple.
		round_to: Rounds the value of each color component to this many decimal places. Setting this
			parameter to 0 ensures that the components will be of type ``int``. The default, -1,
			means that the components won't be rounded at all.
	"""

	def __new__(cls, h: float, s: float, v: float, a: float = None, h_norm=360, sva_norm=1, include_a=False,
	            round_to=-1):
		if a is None:
			a = sva_norm

		if h > h_norm:
			raise ValueError("'h' parameter of HSLColor can't be larger then the defined 'h_norm' parameter'")
		if any(spec > sva_norm for spec in (s, v, a)):
			raise ValueError(
				"'s', 'v' and 'a' parameters of HSLColor can't be larger then the defined 'sva_norm' parameter'")

		rgba = colorsys.hsv_to_rgb(h / h_norm, s / sva_norm, v / sva_norm) + (a / sva_norm,)
		obj = super().__new__(cls, (h, s, v, a), rgba, include_a=include_a, round_to=round_to)
		obj.h_norm = h_norm
		obj.sva_norm = sva_norm

		return obj

	def __init__(self, **kwargs):
		pass

	@classmethod
	def _from_rgba(cls, rgba, h_norm=360, sva_norm=1, include_a=False, round_to=-1):
		hsv = colorsys.rgb_to_hsv(*rgba[:-1])
		hsva = (hsv[0] * h_norm, hsv[1] * sva_norm, hsv[2] * sva_norm, rgba[-1] * sva_norm)

		obj = super().__new__(cls,
		                      hsva,
		                      rgba,
		                      include_a=include_a,
		                      round_to=round_to)
		obj.h_norm = h_norm
		obj.sva_norm = sva_norm
		return obj


class CMYKColor(ColorTupleBase):
	"""Represents a color in the `CMYK color space`_.

	.. _CMYK color space: https://en.wikipedia.org/wiki/CMYK_color_model

	Args:
		c: Cyan component of the color.
		m: Magenta component of the color.
		y: Yellow component of the color.
		k: Key (black) component of the color.
		a: Opacity component of the color. Defaults to ``None``, which means it will be the same
			as the ``norm`` parameter.
		norm: What the ``c``, ``m``, ``y``, ``k``, and ``a`` components are normalized to (aka
			their highest possible value). Some common values for this parameter would be 1 or
			100.
		include_a: Whether to include the opacity parameter ``a`` in the contructed tuple.
			Setting it to ``True`` may result in an object such as :code:`CMYKColor(1, 1, 0,
			1)` instead of :code:`CMYKColor(1, 1, 0)`, for exemple.
		round_to: Rounds the value of each color component to this many decimal places. Setting
			this parameter to 0 ensures that the components will be of type ``int``. The default,
			-1, means that the components won't be rounded at all.
	"""

	def __new__(cls, c: float, m: float, y: float, k: float, a: float = None, norm=1, include_a=False,
	            round_to=-1):
		if a is None:
			a = norm

		if any(spec > norm for spec in (c, m, y, k, a)):
			raise ValueError("'c', 'm', 'y', 'k' and 'a' parameters of CMYKColor can't be larger then"
			                 " the defined 'norm' parameter'")

		r = (1 - c / norm) * (1 - k / norm)
		g = (1 - m / norm) * (1 - k / norm)
		b = (1 - y / norm) * (1 - k / norm)

		obj = super().__new__(cls, (c, m, y, k, a), (r, g, b, a / norm), include_a=include_a, round_to=round_to)
		obj.norm = norm

		return obj

	def __init__(self, **kwargs):
		pass

	@classmethod
	def _from_rgba(cls, rgba, norm=1, include_a=False, round_to=-1):
		if sum(rgba[:-1]) == 0:
			cmyka = (0, 0, 0, norm, rgba[-1] * norm)

		else:
			c = 1 - rgba[0]
			m = 1 - rgba[1]
			y = 1 - rgba[2]

			k = min(c, m, y)
			c = (c - k) / (1 - k)
			m = (m - k) / (1 - k)
			y = (y - k) / (1 - k)
			cmyka = [spec * norm for spec in (c, m, y, k, rgba[-1])]

		obj = super().__new__(cls,
		                      cmyka,
		                      rgba,
		                      include_a=include_a,
		                      round_to=round_to)
		obj.norm = norm
		return obj


class CMYColor(ColorTupleBase):
	"""Represents a color in the `CMY color space`_.

	.. _CMY color space: https://en.wikipedia.org/wiki/CMY_color_model


	Args:
		c: Cyan component of the color.
		m: Magenta component of the color.
		y: Yellow component of the color.
		a: Opacity component of the color. Defaults to ``None``, which means it will be the same
			as the ``norm`` parameter.
		norm: What the ``c``, ``m``, ``y`` and ``a`` components are normalized to (aka
			their highest possible value). Some common values for this parameter would be 1 or
			100.
		include_a: Whether to include the opacity parameter ``a`` in the contructed tuple.
			Setting it to ``True`` may result in an object such as :code:`CMYColor(1, 1, 0,
			1)` instead of :code:`CMYColor(1, 1, 0)`, for exemple.
		round_to: Rounds the value of each color component to this many decimal places. Setting
			this parameter to 0 ensures that the components will be of type ``int``. The default,
			-1, means that the components won't be rounded at all.
	"""

	def __new__(cls, c: float, m: float, y: float, a: float = None, norm=1, include_a=False,
	            round_to=-1):
		if a is None:
			a = norm

		if any(spec > norm for spec in (c, m, y, a)):
			raise ValueError("'c', 'm', 'y' and 'a' parameters of CMYColor can't be larger then"
			                 " the defined 'norm' parameter'")

		obj = super().__new__(cls,
		                      (c, m, y, a),
		                      (1 - c / norm, 1 - m / norm, 1 - y / norm, a / norm),
		                      include_a=include_a,
		                      round_to=round_to)
		obj.norm = norm

		return obj

	def __init__(self, **kwargs):
		pass

	@classmethod
	def _from_rgba(cls, rgba, norm=1, include_a=False, round_to=-1):

		obj = super().__new__(cls,
		                      [spec * norm for spec in (1 - rgba[0], 1 - rgba[1], 1 - rgba[2], rgba[-1])],
		                      rgba,
		                      include_a=include_a,
		                      round_to=round_to)
		obj.norm = norm
		return obj


class HexColor(ColorBase, str):
	"""Represents a color in the `RGB color space`_ as a hexadecimal string.

	Is mostly used for representing `colors in web applications`_.

	.. _colors in web applications: https://en.wikipedia.org/wiki/Web_colors

	Args:
		hex_str: Hexadecimal string from which the ``HexColor`` instance will be built.
			May or may not include a "#" character in its beggining.
		include_a: Whether to include the opacity parameter ``a`` in the contructed tuple.
			Setting it to ``True`` may result in an object such as :code:`HexColor('#ffffff00')`
			instead of :code:`HexColor('#ffff00')`, for exemple.
	"""

	def __new__(cls, hex_str: str, include_a=False):
		hex_str = hex_str.lstrip("#")
		if len(hex_str) == 6:
			a = 1
		elif len(hex_str) == 8:
			a = int(hex_str[:2], 16) / 255
		else:
			raise ValueError("'hex_str' parameter of 'HexColor' class should be either 6 or 8 characters long "
			                 "(disregarding the '#' at the begging)")
		rgb = tuple(int(hex_str[i:i + 2], 16) / 255 for i in (-6, -4, -2))

		obj = str.__new__(cls, hex_str)
		obj._rgba = rgb + (a,)
		return obj

	def __init__(self, **kwargs):
		pass

	def __repr__(self):
		return f"{self.__class__.__name__}({str.__repr__(self)})"

	def __eq__(self, other):
		return ColorBase.__eq__(self, other) if isinstance(other, ColorBase) else str.__eq__(self, other)

	@classmethod
	def _from_rgba(cls, rgba, include_a=False):
		rgba_ = tuple([int(spec * 255) for spec in rgba])
		hex_str = '%02x%02x%02x' % rgba_[:3]
		if not include_a:
			hex_str = '#' + hex_str
		else:
			hex_str = '#%02x' % rgba_[-1] + hex_str

		obj = str.__new__(cls, hex_str)
		obj.include_a = include_a
		obj._rgba = tuple(rgba)
		return obj
