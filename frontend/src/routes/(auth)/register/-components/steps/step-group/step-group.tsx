import { useTranslate } from "@kanjou/react";

import {
  HeroButton,
  Loader,
  HeroSelect,
  HeroSelectContent,
  HeroSelectItem,
  HeroSelectTrigger,
  HeroSelectValue,
  Typography,
} from "#/components/ui";

import { RegisterStep } from "../../register-provider";
import { MistakeCaption } from "../components/mistake-caption";
import { useStepGroup } from "./hooks";

export function StepGroup() {
  const { state, queries, features } = useStepGroup();

  const t = useTranslate();

  return (
    <form
      className="flex flex-1 flex-col"
      onSubmit={(event) => {
        event.preventDefault();
        void features.form.handleSubmit();
      }}
    >
      <Typography variant="title">{t("step.course-select.title")}</Typography>
      <features.form.Field
        name="courseName"
        validators={{
          onSubmit: ({ value }) => (value === "" ? "field.course.error.empty" : undefined),
        }}
        listeners={{
          onChange: () => features.form.setFieldValue("groupId", ""),
        }}
      >
        {(field) => (
          <HeroSelect
            items={state.courses}
            value={field.state.value}
            onValueChange={(value) => field.handleChange(value ?? "")}
          >
            <HeroSelectTrigger className="mt-2" aria-invalid={field.state.meta.errors.length > 0}>
              <HeroSelectValue placeholder={t("field.course.placeholder")} />
            </HeroSelectTrigger>
            <HeroSelectContent>
              {queries.courses.isPending && <Loader />}
              {state.courses?.map((item) => (
                <HeroSelectItem key={item.value} value={item.value}>
                  {item.label}
                </HeroSelectItem>
              ))}
            </HeroSelectContent>
          </HeroSelect>
        )}
      </features.form.Field>
      <Typography className="mt-8" variant="caption">
        {t("field.group.label")}
      </Typography>
      <features.form.Field
        name="groupId"
        validators={{
          onSubmit: ({ value }) => (value === "" ? "field.group.error.empty" : undefined),
        }}
      >
        {(field) => (
          <HeroSelect
            items={state.groups}
            value={field.state.value}
            onValueChange={(value) => field.handleChange(value ?? "")}
          >
            <HeroSelectTrigger
              className="mt-2"
              disabled={!state.courseName}
              aria-invalid={!!field.state.meta.errors.length && !!state.courseName}
            >
              <HeroSelectValue placeholder={t("field.group.placeholder")} />
            </HeroSelectTrigger>
            <HeroSelectContent>
              {state.groups?.map((item) => (
                <HeroSelectItem key={item.value} value={item.value}>
                  {item.label}
                </HeroSelectItem>
              ))}
            </HeroSelectContent>
          </HeroSelect>
        )}
      </features.form.Field>

      <div className="flex-1 flex flex-col justify-end">
        <HeroButton type="submit">{t("action.next.title")}</HeroButton>
        <MistakeCaption to={RegisterStep.Name} />
      </div>
    </form>
  );
}
