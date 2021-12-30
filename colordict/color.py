import colorsys
import abc


class ColorBase(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __new__(cls, rgba):
		obj = super().__new__(cls)
		obj._rgba = tuple(rgba)
		return obj

	@classmethod
	@abc.abstractmethod
	def _from_rgba(cls, rgba, **kwargs):
		# Factory method to be called when reading the palette files
		pass

	def hex(self, **kwargs):
		return HexColor._from_rgba(self._rgba, **kwargs)

	def rgb(self, **kwargs):
		return sRGBColor._from_rgba(self._rgba, **kwargs)

	def hsl(self, **kwargs):
		return HSLColor._from_rgba(self._rgba, **kwargs)

	def hsv(self, **kwargs):
		return HSVColor._from_rgba(self._rgba, **kwargs)


class ColorTupleBase(tuple, ColorBase, metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __new__(cls, iterable, rgba, include_a=False, rounded=-1):
		if not include_a:
			iterable = iterable[:-1]
		if rounded != -1:
			iterable = [round(val, rounded) for val in iterable]
		obj = tuple.__new__(cls, iterable)
		obj._rgba = tuple(rgba)
		obj.include_a = include_a
		obj.rounded = rounded

		return obj

	def __repr__(self):
		return f"{self.__class__.__name__}{tuple.__repr__(self)}"


class sRGBColor(ColorTupleBase):
	def __new__(cls, r, g, b, a=None, norm=255, include_a=False, rounded=-1):
		if a is None:
			a = norm

		obj = super().__new__(cls,
		                      (r, g, b, a),
		                      (r / norm, g / norm, b / norm, a / norm),
		                      include_a=False,
		                      rounded=rounded)
		obj.norm = norm
		return obj

	@classmethod
	def _from_rgba(cls, rgba, norm=255, include_a=False, rounded=-1):
		rgba_ = [spec * norm for spec in rgba]
		obj = super().__new__(cls,
		                      rgba_,
		                      rgba,
		                      include_a=include_a,
		                      rounded=rounded)
		obj.norm = norm
		return obj


class HSLColor(ColorTupleBase):
	def __new__(cls, h, s, l, a=None, h_norm=360, sla_norm=1, include_a=False, rounded=-1):
		if a is None:
			a = sla_norm

		rgba = colorsys.hls_to_rgb(h / h_norm, l / sla_norm, s / sla_norm) + (a / sla_norm,)
		obj = super().__new__(cls, (h, s, l, a), rgba, include_a=include_a, rounded=rounded)
		obj.h_norm = h_norm
		obj.sla_norm = sla_norm

		return obj

	@classmethod
	def _from_rgba(cls, rgba, h_norm=360, sla_norm=1, include_a=False, rounded=-1):
		hls = colorsys.rgb_to_hls(*rgba[:-1])
		hsla = (hls[0] * h_norm, hls[2] * sla_norm, hls[1] * sla_norm, rgba[-1] * sla_norm)

		obj = super().__new__(cls,
		                      hsla,
		                      rgba,
		                      include_a=include_a,
		                      rounded=rounded)
		obj.h_norm = h_norm
		obj.sla_norm = sla_norm
		return obj


class HSVColor(ColorTupleBase):
	def __new__(cls, h, s, v, a=None, h_norm=360, sva_norm=1, include_a=False, rounded=-1):
		if a is None:
			a = sva_norm

		rgba = colorsys.hsv_to_rgb(h / h_norm, s / sva_norm, v / sva_norm) + (a / sva_norm,)
		obj = super().__new__(cls, (h, s, v, a), rgba, include_a=include_a, rounded=rounded)
		obj.h_norm = h_norm
		obj.sva_norm = sva_norm

		return obj

	@classmethod
	def _from_rgba(cls, rgba, h_norm=360, sva_norm=1, include_a=False, rounded=-1):
		hsv = colorsys.rgb_to_hsv(*rgba[:-1])
		hsva = (hsv[0] * h_norm, hsv[1] * sva_norm, hsv[2] * sva_norm, rgba[-1] * sva_norm)

		obj = super().__new__(cls,
		                      hsva,
		                      rgba,
		                      include_a=include_a,
		                      rounded=rounded)
		obj.h_norm = h_norm
		obj.sva_norm = sva_norm
		return obj


class HexColor(str, ColorBase):
	def __new__(cls, hex_str, include_a=False):
		hex_str = hex_str.lstrip("#")
		if len(hex_str) == 6:
			a = 1
		elif len(hex_str) == 8:
			a = int(hex_str[:2], 16) / 255
		else:
			raise ValueError("'hex_str' parameter of 'HexColor' class should be either 6 or 8 characters long "
			                 "(disregarding the '#' at the begging)")
		rgb = [int(hex_str[i:i + 2], 16) / 255 for i in (-6, -4, -2)]

		obj = str.__new__(cls, hex_str)
		obj._rgba = (*rgb, a)
		return obj

	def __repr__(self):
		return f"{self.__class__.__name__}({str.__repr__(self)})"

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
		obj._rgba = rgba
		return obj