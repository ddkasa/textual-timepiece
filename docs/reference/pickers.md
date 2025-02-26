!!! note
    These pickers are built through a combination of [selectors](selectors.md) & [input](input.md) widgets, so in order to get a full understanding of the widgets functionality its recommend to the read aforementioned pages.

!!! info
    All pickers have a `.mini` CSS class which you can assign to these widgets, to convert them to a single line.


<details>

<summary>Picker Default TCSS</summary>

<p>Most pickers use the Textual CSS below as their base with minimal modifications.</p>

```CSS
AbstractPicker {
    layers: base dialog;
    layout: vertical;
    height: 3;
    width: auto;

    &.mini {
        max-height: 1;
        & > #input-control {
            border: none;
            height: 1;
            padding: 0;

            &:blur {
                padding: 0;
            }
            &:focus-within {
                padding: 0;
                border: none;
            }
            Button, AbstractInput {
                border: none;
                padding: 0;
                height: 1;

                &:focus {
                    color: $accent;
                    text-style: none;
                }
                &:disabled {
                    opacity: 50%;
                    text-style: italic;
                }
            }
        }
    }

    & > #input-control {
        background: $surface;
        width: auto;

        &:blur {
            padding: 1;
        }
        &:focus-within {
            border: tall $primary;
            padding: 0;
        }

        Button, AbstractInput {
            border: none;
            padding: 0;
            height: 1;

            &:focus {
                color: $accent;
                text-style: none;
            }
        }
        & > TargetButton {
            min-width: 1;
            max-width: 3;
        }

        & > AbstractInput {
            padding: 0 2;
            &.-invalid {
                color: $error;
                text-style: italic;
            }
            &:focus {
                tint: $primary 2%;
            }
        }
    }
    & > BaseOverlay {
        constrain: inside;
        border: round $secondary;
        height: auto;
        width: auto;
        background: $surface;
        box-sizing: content-box;
        opacity: 0;

        &:focus,
        &:focus-within {
            border: round $primary;
        }

        & > BaseOverlayWidget {
            width: 40;
            height: auto;
        }
    }
}
```

</details>

---

::: textual_timepiece.pickers.DatePicker

---

::: textual_timepiece.pickers.DurationPicker

---

::: textual_timepiece.pickers.TimePicker

---

::: textual_timepiece.pickers.DateTimePicker

---

::: textual_timepiece.pickers.DateRangePicker

---

::: textual_timepiece.pickers.DateTimeRangePicker

---

::: textual_timepiece.pickers.DateTimeDurationPicker
