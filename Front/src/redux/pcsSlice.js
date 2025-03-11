import { createSlice } from "@reduxjs/toolkit";

// Initial state for managing PCs
const initialState = {
  pcs: Array.from({ length: 100 }, (_, index) => ({
    id: `PC-${index + 1}`,
    ip: `10.20.9.${index + 1}`,
    mac: `00:1A:2B:3C:4D:${index.toString().padStart(2, "0")}`,
    status:
      Math.random() > 0.8
        ? "disconnected"
        : Math.random() > 0.6
        ? "restricted"
        : "active",
  })),
};
/*
[{ id: "PC-1", ip: "10.20.9.12", mac: "", status: "active" }],
  */

const pcsSlice = createSlice({
  name: "pcs",
  initialState,
  reducers: {
    updatePC: (state, action) => {
      const { id, updatedData } = action.payload;
      const pcIndex = state.pcs.findIndex((pc) => pc.id === id);
      if (pcIndex !== -1) {
        state.pcs[pcIndex] = { ...state.pcs[pcIndex], ...updatedData };
      } else {
        console.error("PC not found for update");
      }
    },
  },
});

export const { updatePC } = pcsSlice.actions;
export default pcsSlice.reducer;
