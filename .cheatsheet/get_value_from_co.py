# -*- coding: utf-8 -*-
def get_value_from_co(co):
    try:
        co.send(None)
    except StopIteration as err:
        return err.value
