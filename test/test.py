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

    # ui_in[0] == 0: Output is uio_in
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut.uio_in.value[7] = 1;

    temp = 0

    for i in range(128):
        temp = dut.uo_out.value
        dut.uio_in.value[0:7] = i
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value[0:7] == i
        assert dut.uo_out.value[7] == ~temp[0]

    # When under reset: Output is uio_in, uio is in input mode
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 1)

    dut.uio_in.value[7] = 0;

    for i in range(128):
        temp = dut.uo_out.value
        dut.uio_in.value[0:7] = i
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value[0:7] == temp[1:8]
        assert dut.uo_out.value[7] == ~temp[0]

@cocotb.test()
async def test_counter(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # ui_in[0] == 1: bidirectional outputs enabled, put a counter on both output and bidirectional pins
    dut.ui_in.value = 1
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
