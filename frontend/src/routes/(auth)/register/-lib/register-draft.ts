import type { RegisterState } from "../-components/register-provider";
import { LOCALSTORAGE_REGISTER_STATE } from "../-constants";

export const DEFAULT_REGISTER_STATE: RegisterState = { step: "name" };

export const registerDraft = {
  load(): RegisterState {
    try {
      const draft = localStorage.getItem(LOCALSTORAGE_REGISTER_STATE);

      if (draft) return JSON.parse(draft);
    } catch {
      this.clear();
    }

    return DEFAULT_REGISTER_STATE;
  },
  save(state: RegisterState) {
    localStorage.setItem(LOCALSTORAGE_REGISTER_STATE, JSON.stringify(state));
  },
  clear() {
    localStorage.removeItem(LOCALSTORAGE_REGISTER_STATE);
  },
};
