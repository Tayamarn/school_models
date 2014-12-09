from itravel import ITravel


class MockML(object):
    def check_model(self, model):
        pass

    def check_input_params(self, model, input_params):
        pass

    def check_model_params(self, model, model_params):
        pass

    def check_components(self, model, components):
        pass

    def check_interm_params(self, model, interm_params, hidden_params):
        pass

ml = MockML()

s = ITravel(ml, 'foo', 'logger', 'out')
inp = {'dimensions': '3D', 'device_class': 'tourist'}
q = s.team_arguments(inp)
print(q)
print(s.compute_3d(q))
