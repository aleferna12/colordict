

def _lin_interp(c1, c2, t):
    return tuple([c1[i] + (c2[i] - c1[i])*t for i in range(len(c1))])


class LinearGrad(object):
    def __init__(self, color_values):
        if type(color_values) == list or type(color_values) == tuple:
            raise TypeError(f"type {type(color_values)} does not conform to the expected list or tuple types")
        super().__init__()
        self.colors = color_values

    def __call__(self, p):
        i = int(p*(len(self.colors) - 1))
        return _lin_interp(self.colors[i], self.colors[min([i + 1, len(self.colors) - 1])], p*(len(self.colors) - 1) - i)

    def n_colors(self, n, stripped=True):
        colors = []
        sub = 1 if stripped else -1
        for i in range(n):
            p = (i + stripped) / (n + sub)
            colors.append(self.__call__(p))
        return colors