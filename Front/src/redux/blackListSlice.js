import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    blackListedIPs: [],
};

const blackListSlice = createSlice({
    name: "blacklist",
    initialState, 
    reducers: {
        addToBlackList: (state, action) => {
            state.blackListedIPs.push(action.payload)
        }
    }
});

export const {addToBlackList} = blackListSlice.actions;
export default blackListSlice.reducer;