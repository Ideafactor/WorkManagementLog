import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LoginForm } from "./LoginForm";

describe("LoginForm", () => {
  it("submits normalized email and the entered password", () => {
    const onSubmit = vi.fn();
    render(<LoginForm busy={false} error={null} onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText("이메일"), {
      target: { value: " admin@example.com " },
    });
    fireEvent.change(screen.getByLabelText("비밀번호"), {
      target: { value: "a-long-local-password" },
    });
    fireEvent.click(screen.getByRole("button", { name: "로그인" }));

    expect(onSubmit).toHaveBeenCalledWith(
      "admin@example.com",
      "a-long-local-password",
    );
  });
});
