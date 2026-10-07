import { useTranslate } from "@kanjou/react";
import { useForm, useSelector } from "@tanstack/react-form";

import { useGetCoursesCourseGet } from "#/api/hooks";

import { RegisterStep, useRegisterContext } from "../../../register-provider";

export function useStepGroup() {
  const t = useTranslate();

  const register = useRegisterContext();

  const coursesQuery = useGetCoursesCourseGet();

  const form = useForm({
    defaultValues: {
      courseName: register.state.courseName ?? "",
      groupId: register.state.groupId?.toString() ?? "",
    },
    onSubmit: ({ value }) => {
      register.goTo(RegisterStep.Avatar, {
        groupId: +value.groupId,
        courseName: value.courseName,
      });
    },
  });

  const courseName = useSelector(form.store, (state) => state.values.courseName);

  const courses = coursesQuery.data?.map((course) => ({
    label: course.name,
    value: course.name,
  }));
  const groups = coursesQuery.data
    ?.find((course) => course.name === courseName)
    ?.groups?.map((group) => ({
      label: `${t("text.group")} ${group}`,
      value: `${group}`,
    }));

  return {
    state: {
      courseName,
      courses,
      groups,
    },
    queries: {
      courses: coursesQuery,
    },
    mutations: {},
    functions: {},
    features: {
      form,
    },
  };
}
