import { stylelint } from "@iivanpopov/stylelint";

export default stylelint({
  rules: {
    "no-empty-source": [true, { severity: "warning" }],
    "block-no-empty": [true, { severity: "warning" }],
  },
});
