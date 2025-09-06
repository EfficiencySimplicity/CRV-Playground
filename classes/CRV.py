from classes.Utils import *

################ Composite Representation Vectors ################

class CRV:
    
    PRINT_CUTOFF_AMT = 20
    PRINT_ROUND_DIGITS = 2

    
    def __init__(self, values):
        self.vals = sort_abs_hl(values)


    # Plotting

    def plot(self, mode = 'pie', start = 0, length = 20):
        plot_dict(sort_abs_hl(self.vals), mode = mode, start = start, length = length)
        

    # Dunder methods
    
    def asdict(self):
        return dict(self.vals)
    
    def __iter__(self):
        for key in self.keys():
            yield key

    def min(self, other):
        if type(other) in (int, float):
            return {k : min(v, other) for k, v in self.items()}
        else:
            return {k : min(self[k], other[k]) for k in set(self.keys()).intersection(other.keys())}
    
    def __abs__(self):
        return CRV(self._abs(self.asdict()))
    
    def _abs(self, d):
        return {key : abs(value) for key, value in d.items()}
    
    def _add(self, d, d2):
        return {key : d.get(key, 0) + d2.get(key, 0) for key in set(d.keys()).union(d2.keys())}
    
    def _sadd(self, d, s):
        return {key : value + s for key, value in d.items()}
    
    def _sub(self, d, d2):
        return {key : d.get(key, 0) - d2.get(key, 0) for key in set(d.keys()).union(d2.keys())}
    
    def _ssub(self, d, s):
        return {key : value - s for key, value in d.items()}
    
    def _rsub(self, d, d2):
        return self._sub(d2, d)
    
    def _rssub(self, d, s):
        return {key : s - value for key, value in d.items()}
    
    def _mul(self, d, d2):
        return {key : d[key] * d2[key] for key in set(d.keys()).intersection(d2.keys())}
    
    def _smul(self, d, s):
        return {key : value * s for key, value in d.items()}
    
    def _div(self, d, d2):
        return {key : d[key] / d2[key] for key in set(d.keys()).intersection(d2.keys())}
    
    def _sdiv(self, d, s):
        return {key : value / s for key, value in d.items()}
    
    def _rdiv(self, d, d2):
        return self._div(d2, d)
    
    def _rsdiv(self, d, s):
        return {key : s / value for key, value in d.items()}
    
    def _pow(self, d, d2):
        return {key : d[key] ** d2[key] for key in set(d.keys()).union(d2.keys())}
    
    def _spow(self, d, s):
        return {key : value ** s for key, value in d.items()}
    
    def _rpow(self, d, d2):
        return self._pow(d2, d)
    
    def _rspow(self, d, s):
        return {key : s ** value for key, value in d.items()}

    
    def __add__(self, other):
        if type(other) in (int, float):
            return CRV(self._sadd(self.vals, other))
        else:
            return CRV(self._add(self.vals, dict(other)))

    
    def __sub__(self, other):
        if type(other) in (int, float):
            return CRV(self._ssub(self.vals, other))
        else:
            return CRV(self._sub(self.vals, dict(other)))

    def __rsub__(self, other):
        if type(other) in (int, float):
            return CRV(self._rssub(self.vals, other))
        else:
            return CRV(self._rsub(self.vals, dict(other)))

    
    def __mul__(self, other):
        if type(other) in (int, float):
            return CRV(self._smul(self.vals, other))
        else:
            return CRV(self._mul(self.vals, dict(other)))

    
    def __truediv__(self, other):
        if type(other) in (int, float):
            return CRV(self._sdiv(self.vals, other))
        else:
            return CRV(self._div(self.vals, dict(other)))
        
    def __rtruediv__(self, other):
        if type(other) in (int, float):
            return CRV(self._rsdiv(self.vals, other))
        else:
            return CRV(self._rdiv(self.vals, dict(other)))

    
    def __pow__(self, other):
        if type(other) in (int, float):
            return CRV(self._spow(self.vals, other))
        else:
            return CRV(self._pow(self.vals, dict(other)))
        
    def __rpow__(self, other):
        if type(other) in (int, float):
            return CRV(self._rspow(self.vals, other))
        else:
            return CRV(self._rpow(self.vals, dict(other)))



    __radd__ = __add__
    __rmul__ = __mul__

    
    # Get and Set
    
    def __getitem__(self, index):
        return self.vals.get(index, 0)

    def __setitem__(self, index, value):
        self.vals[index] = value

    def pop(self, key):
        return self.vals.pop(key, None)

    def items(self):
        return self.vals.items()
    
    def keys(self):
        return self.vals.keys()
    
    def values(self):
        return self.vals.values()


    # Printing
    
    def __repr__(self):
        
        repr_string = ''
        cutoff = self.PRINT_CUTOFF_AMT
        
        for key, val in self.items():
            repr_string += f' {'+' if val >= 0 else '-'} \033[94m{abs(round(val, self.PRINT_ROUND_DIGITS))}\033[37m\u22C5\033[92m{'\\n' if key == '\n' else key}\033[37m'
            cutoff -= 1

            if cutoff == 0 and len(self.items()) != self.PRINT_CUTOFF_AMT:
                repr_string += f' + \033[96m{len(self.items()) - self.PRINT_CUTOFF_AMT}\033[37m \033[31mothers\033[37m'
                break

        return '{' + repr_string + '}'
    
    def print_full(self):
        for key, val in self.items():
            print(f'{'+' if val >= 0 else '-'} \033[94m{abs(round(val, self.PRINT_ROUND_DIGITS))}\033[37m\u22C5\033[92m{'\\n' if key == '\n' else key}\033[37m')
            