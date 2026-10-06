import { Link } from "@tanstack/react-router";
import { useTranslate } from "@kanjou/react";
import { ReactNode } from "react";

import { Button, HeroInput, Typography } from "#/components/ui";

import { useStepName } from "./hooks";

import styles from "./step-name.module.css";

const components = {
  a: ({ children }: { children: ReactNode }) => (
    <Link to="/login" className={styles.link}>
      {children}
    </Link>
  ),
};

export function StepName() {
  const { functions, features } = useStepName();

  const t = useTranslate();

  return (
    <div className="flex flex-1 flex-col">
      <Typography variant="title">{t("action.registration.title")}</Typography>
      <Typography variant="caption">
        {t("action.registration.description")}
      </Typography>
      <HeroInput
        {...features.nameField.register()}
        placeholder={t("field.name.placeholder")}
        className="mt-4"
      />

      <div className="flex-1 flex flex-col justify-end">
        <Button
          onClick={functions.handleRegister}
          variant="hero"
          className="w-full"
        >
          {t("action.start.title")}
        </Button>
        <Typography variant="caption" className="text-center mt-4">
          {t.rich("caption.has-account", undefined, { components })}
        </Typography>
      </div>
    </div>
  );
}
