# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_loopback(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1

    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut.ui_in.value = (1 << 7)
    await ClockCycles(dut.clk, 1)
    assert (dut.ui_in.value[1:7] == 0), (
        f"Expected bit 6:0 to be 0, but got {int(dut.ui_in.value[1:7])}. "
        f"Full input: {dut.ui_in.value}"
    )
    assert (dut.ui_in.value[0] == 1), (
        f"Expected bit 7 to be 1, but got {dut.ui_in.value[0]}. "
        f"Full input: {dut.ui_in.value}"
    )

    temp = 0

    for i in range(128):
        temp = dut.uo_out.value
        dut.ui_in.value = ((dut.ui_in.value & 0x80) | (i & 0x7F))
        await ClockCycles(dut.clk, 1)
        assert (dut.ui_in.value[1:7] == i), (
            f"Test failed at iteration {i}: "
            f"Expected bit 6:0 to be {i}, but got {dut.ui_in.value[1:7]}. "
            f"Full input: {dut.ui_in.value}"
        )
        assert (dut.ui_in.value[0] == 1), (
            f"Test failed at iteration {i}: "
            f"Expected bit 7 to be 1, but got {dut.ui_in.value[7]}. "
            f"Full input: {dut.ui_in.value}"
        )
        if i != 0:
            assert (dut.uo_out.value[1:7] == i-1), (
                f"Test failed at iteration {i}: "
                f"Expected bit 6:0 to be {i-1}, but got {dut.uo_out.value[1:7]}. "
                f"Full output: {dut.uo_out.value}, Input: {dut.ui_in.value}"
            )
            assert (dut.uo_out.value[0] == ~temp[7]), (
                f"Test failed at iteration {i}: "
                f"Expected bit 7 to be {~temp[7]}, but got {dut.uo_out.value[0]}. "
                f"Full output: {dut.uo_out.value}, Previous output: {temp}"
            )
    temp = dut.uo_out.value
    await ClockCycles(dut.clk, 1)
    assert (dut.uo_out.value[1:7] == 127), (
        f"Test failed at iteration 127: "
        f"Expected bit 6:0 to be 127, but got {dut.uo_out.value[1:7]}. "
        f"Full output: {dut.uo_out.value}, Input: {dut.ui_in.value}"
    )
    assert (dut.uo_out.value[0] == ~temp[7]), (
        f"Test failed at iteration 127: "
        f"Expected bit 7 to be {~temp[7]}, but got {dut.uo_out.value[0]}. "
        f"Full output: {dut.uo_out.value}, Previous output: {temp}"
    )

    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    assert (dut.ui_in.value[1:7] == 0), (
        f"Expected bit 6:0 to be 0, but got {dut.ui_in.value[1:7]}. "
        f"Full input: {dut.ui_in.value}"
    )
    assert (dut.ui_in.value[0] == 0), (
        f"Expected bit 7 to be 0, but got {dut.ui_in.value[0]}. "
        f"Full input: {dut.ui_in.value}"
    )

    for i in range(128):
        temp = dut.uo_out.value
        dut.ui_in.value = ((dut.ui_in.value & 0x80) | (i & 0x7F))
        await ClockCycles(dut.clk, 1)
        assert (dut.ui_in.value[1:7] == i), (
            f"Test failed at iteration {i}: "
            f"Expected bit 6:0 to be {i}, but got {dut.ui_in.value[1:7]}. "
            f"Full input: {dut.ui_in.value}"
        )
        assert (dut.ui_in.value[0] == 0), (
            f"Test failed at iteration {i}: "
            f"Expected bit 7 to be 0, but got {dut.ui_in.value[0]}. "
            f"Full input: {dut.ui_in.value}"
        )
        assert (dut.uo_out.value[1:7] == temp[0:6]), (
            f"Test failed at iteration {i}: "
            f"Expected bit 6:0 to be {temp[0:6]}, but got {dut.uo_out.value[1:7]}. "
            f"Full output: {dut.uo_out.value}, Previous output: {temp}"
        )
        assert (dut.uo_out.value[0] == ~temp[7]), (
            f"Test failed at iteration {i}: "
            f"Expected bit 7 to be {~temp[7]}, but got {dut.uo_out.value[0]}. "
            f"Full output: {dut.uo_out.value}, Previous output: {temp}"
        )

@cocotb.test()
async def test_counter(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    dut._log.info("Testing counter")
    for i in range(256):
        assert dut.uo_out.value == dut.uio_out.value
        await ClockCycles(dut.clk, 1)

    dut._log.info("Testing reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    assert dut.uo_out.value == 0
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
