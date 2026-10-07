import { useTranslate } from "@kanjou/react";
import { ReactNode } from "react";

import { Button, Typography } from "#/components/ui";

import { RegisterStep, useRegisterContext } from "../../../register-provider";

interface BackProps {
  to: RegisterStep;
  children: ReactNode;
}

function Back({ children, to }: BackProps) {
  const register = useRegisterContext();

  return (
    <Button variant="link" onClick={() => register.goTo(to)}>
      <Typography variant="caption">{children}</Typography>
    </Button>
  );
}

export interface MistakeCaptionProps {
  to: RegisterStep;
}

export function MistakeCaption({ to }: MistakeCaptionProps) {
  const t = useTranslate();

  return (
    <Typography variant="caption" className="text-center mt-4">
      {t.rich("caption.mistake", { to }, { components: { a: Back } })}
    </Typography>
  );
}
