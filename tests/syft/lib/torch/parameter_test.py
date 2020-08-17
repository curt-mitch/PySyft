import syft as sy
import torch as th


def test_parameter_vm_remote_operation():

    alice = sy.VirtualMachine(name="alice")
    alice_client = alice.get_client()

    x = th.nn.Parameter(th.randn(3, 3))

    xp = x.send(alice_client)

    y = xp + xp

    assert len(alice.store._objects) == 2

    y.get()

    assert len(alice.store._objects) == 1

    # TODO: put thought into garbage collection and then
    #  uncoment this.
    # del xp
    #
    # assert len(alice.store._objects) == 0


def test_parameter_serde():
    param = th.nn.parameter.Parameter(th.tensor([1.0, 2, 3]), requires_grad=True)
    # Setting grad manually to check it is passed through serialization
    param.grad = th.randn_like(param)

    blob = param.serialize()

    param2 = sy.deserialize(blob=blob)

    assert (param == param2).all()
    assert (param2.grad == param2.grad).all()
    assert param2.requires_grad == param2.requires_grad


def test_linear_grad_serde():
    # Parameter is created inside Linear module
    linear = th.nn.Linear(5, 1)
    param = linear.weight
    assert hasattr(param, "id")

    # Induce grads on linear weights
    out = linear(th.randn(5, 5))
    out.backward()
    assert param.grad is not None

    blob = param.serialize()

    param2 = sy.deserialize(blob=blob)

    assert (param == param2).all()
    assert (param2.grad == param2.grad).all()
    assert param2.requires_grad == param2.requires_grad