# Safety & Legal — READ FIRST

OpenCapsule-EDU is an **educational electronics project**. It reproduces the
*architecture* of a capsule endoscope so people can learn from it. It is not,
and must never become, a device used on a living body.

## 1. Absolute rules

1. **Never swallow, insert, or implant** anything built from this project — not the
   full demo pill, not a board, not a battery. Not in humans, not in animals.
2. **The demo shell is intentionally oversized** (30 × 70 mm). Do not miniaturize the
   enclosure to a swallowable size. Pull requests that do so will be rejected.
3. **This project provides no biocompatibility, sterility, or hermeticity** — none of
   the shell materials, adhesives, or coatings here are validated for body contact.
4. **Keep coin cells away from children.** A swallowed button cell causes severe
   chemical burns within hours and is a medical emergency. Store cells in blister
   packs, tape both terminals of spent cells, and dispose of them properly.
5. **No clinical claims.** Nothing produced by this project diagnoses, treats, or
   monitors any medical condition.

## 2. Why a real capsule is a regulated medical device

A real capsule endoscope is a **Class II (FDA) / Class IIa–IIb (EU MDR)** medical
device. Getting one to market requires — among much else — biocompatibility testing
(ISO 10993), electrical safety (IEC 60601-1), risk management (ISO 14971), a quality
system (ISO 13485), sterility validation, and clinical evaluation. This project
teaches the *electronics*; it deliberately does not (and cannot) address any of that.
Understanding this gap is itself one of the learning goals.

## 3. Radio regulations — you are the licensee

The transmitter in this project is a general-purpose sub-1 GHz radio (CC1310). You
are responsible for operating it legally in your region:

| Region | License-free band | Key limits (simplified) |
|---|---|---|
| EU / UK | 433.05–434.79 MHz | ≤ 10 mW e.r.p. |
| EU / UK | 863–870 MHz (868 MHz SRD) | ≤ 25 mW e.r.p., **duty-cycle limits (often ≤ 1 %)** per sub-band |
| USA / Canada | 902–928 MHz (ISM) | FCC Part 15.247 / RSS-247 rules |
| Most regions | 2.4 GHz | not used by this project |

Practical guidance for this project:

- Use your regional band **as configured in the firmware examples** (868 MHz EU profile
  or 915 MHz US profile). Do not simply maximize TX power — the link works across a
  room at 0 dBm.
- **Do not transmit in 402–405 MHz (MedRadio/MICS).** That band is reserved for actual
  medical implants under specific rules; hobby experiments there can interfere with
  real implanted devices.
- Duty-cycle limits in the EU 868 band are conveniently similar to the pulsed operation
  this project teaches anyway — treat the regulation as a design constraint exercise.
- If you modify antennas or amplifiers, you own the compliance consequences.

## 4. Tissue-propagation experiments

Phase 4 suggests studying RF attenuation through **tissue phantoms** — containers of
saline or gelatin with defined salt content. This is the standard, safe, and ethical
way research labs characterize through-body propagation. Do **not** perform
transmission experiments through any living body, including your own hand wrapped
around an active transmitter for hours. Short incidental exposure from a milliwatt-class
device is not the concern; normalizing body-contact experiments is.

## 5. Battery and electrical safety

- Silver-oxide (SR927) and alkaline (LR927) cells are non-rechargeable. **Never charge
  them**, never solder directly to cells (use holders or pre-tabbed cells), never short
  them "to see the spark".
- If a Phase uses Li-ion instead, use protected cells and a proper charger IC.
- Bulk capacitors on the PMU board hold charge after power-off; discharge before rework.

## 6. Intellectual property

The teardown documentation describes *observed engineering* of an unbranded commercial
device for interoperability-free educational analysis, which is generally lawful.
This repository contains **no proprietary firmware, no extracted code, no copied board
layouts**. Contributors must not add dumps of commercial firmware or confidential
documents. Component datasheets are linked, not redistributed.

## 7. Liability

This project and its documentation are provided **“as is”, without warranty of any
kind** (see [LICENSE](LICENSE)). The maintainers and contributors accept no liability
for what you build. If you are ever unsure whether an experiment is safe or legal —
stop and ask in the issues first.
