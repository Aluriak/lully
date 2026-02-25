import lully.texty as ty


def test_basic_api():
    class BaseObject(ty.Rule):
        "(n=Percent|n=NAmongK) kind=/[a-zA-Z]+/"
        def show(self):
            return self.n.show() + ' ' + str(self.kind).upper()
    class Percent(ty.Rule):
        "(q='100'|q=/[0-9]/|q=/[1-9][0-9]/) '%'"
        def show(self):
            return f'{self.q}%'
    class NAmongK(ty.Rule):
        "n=INT ('among'|'in') k=INT"
        def show(self):
            return f'{round(self.n / self.k * 100)}%'  #gg

    assert ty.parse_text('3 in 50 success').show() == '6% SUCCESS'
    assert ty.parse_text('1 in 2 success').show() == '50% SUCCESS'
    assert ty.parse_text('100 in 10 success').show() == '1000% SUCCESS'
    assert ty.parse_text('3% success').show() == '3% SUCCESS'

