module tt_um_johnson (
    input         clk,
    input         rst_n,   // Active-low reset
    input         ena,
    input  [7:0]  ui_in,   // Dedicated input
    output reg [7:0] uo_out,  // Dedicated output
    input  [7:0]  uio_in,  // IO input (unused here)
    output [7:0]  uio_out, // IO output
    output [7:0]  uio_oe   // IO output enable (active high)
);
 
  // For this pass-through design, we simply copy uo_out to uio_out.
  assign uio_out = uo_out;
  // Drive all bits of the IO enable high (active output).
  assign uio_oe = 8'hFF;
 
  // Simple clocked pass-through: when enabled, drive uo_out from ui_in.
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      uo_out <= 8'b0;
    else begin
      uo_out[7] <= ~uo_out[0]
      if (ui_in[7])
        uo_out[6:0] <= ui_in[6:0];
      else
        uo_out[6:0] <= ui_in[7:1];
    end
  end
 
endmodule