export const createSlice = ({ name, initialState, reducers }) => {
  const actions = Object.keys(reducers || {}).reduce((acc, key) => {
    acc[key] = (payload) => ({ type: `${name}/${key}`, payload });
    return acc;
  }, {});
  const reducer = (state = initialState, action) => state;
  return { actions, reducer };
};

export const configureStore = () => ({ dispatch: () => {}, getState: () => ({}) });



