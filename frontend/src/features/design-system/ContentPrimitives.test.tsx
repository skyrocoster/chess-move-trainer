import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";

import { Accordion } from "./Accordion";
import { Avatar } from "./Avatar";
import { ScrollArea } from "./ScrollArea";
import { Separator } from "./Separator";

afterEach(cleanup);

describe("content primitives", () => {
  it("renders and toggles reusable accordion items", async () => {
    const user = userEvent.setup();
    render(
      <Accordion
        items={[
          { value: "idea", summary: "Training idea", content: "Repeat the critical move." },
          { value: "note", summary: "Coach note", content: "Compare both candidate moves." },
        ]}
      />,
    );

    const trigger = screen.getByRole("button", { name: "Training idea" });
    await user.click(trigger);
    expect(trigger).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByText("Repeat the critical move.")).toBeVisible();
  });

  it("shows an avatar fallback when no image is supplied", () => {
    render(<Avatar alt="Alex Morgan" fallback="AM" size="sm" />);
    expect(screen.getByText("AM")).toBeVisible();
  });

  it("keeps scroll-area content in a native viewport", () => {
    render(
      <ScrollArea aria-label="Move history" orientation="both">
        <p>1. e4 e5</p>
      </ScrollArea>,
    );

    expect(screen.getByText("1. e4 e5")).toBeVisible();
    expect(screen.getByLabelText("Move history")).toBeInTheDocument();
  });

  it("exposes separator orientation accessibly", () => {
    render(<Separator orientation="vertical" />);
    expect(screen.getByRole("separator")).toHaveAttribute("aria-orientation", "vertical");
  });
});
