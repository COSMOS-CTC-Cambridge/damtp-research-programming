class directview_class(object):
    '''Dummy class for direct MPI mode'''
    def __setitem__(self, name, value):
        setattr(self, name, value)
    def __getitem__(self, name):
        return getattr(self, name)
    def parallel(self, block=True):
        def passthrough(func):
            def callit(*args, **kwargs):
                return func(*args, **kwargs)
            return callit
        return passthrough
    def remote(self, block=True):
        def passthrough(func):
            def callit(*args, **kwargs):
                return func(*args, **kwargs)
            return callit
        return passthrough
    def apply_async(self, func, *args, **kwargs):
        return func(*args, **kwargs)
