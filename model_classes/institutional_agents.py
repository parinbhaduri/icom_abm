from pynsim import Institution

class CountyZoningManager(Institution):
    def __init__(self, name, **kwargs):
        super(CountyZoningManager, self).__init__(name, **kwargs)

    def determine_zoning(self):
        for bg in self.nodes:
            if bg.pop_density > 0.03:
                bg.zoning = 'not_allowed'

class LeveeManager(Institution):
    def __init__(self, name, **kwargs):
        super(LeveeManager, self).__init__(name, **kwargs)

    def heighten_existing_levee(self):
        pass

    def build_new_levee(self):
        pass