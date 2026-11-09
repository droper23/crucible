"""ESPresso Lab: embedded-flavoured problems designed to be solved in ESPresso."""
import random

TRACK = dict(
    id="espresso-lab",
    title="ESPresso Lab",
    order=18,
    icon="☕",
    blurb="Firmware-style puzzles (debouncing, ring buffers, fixed-point filters, PID) written in ESPresso, the embedded scripting language.",
    intro=r"""
# ESPresso Lab

Every problem in this track is the kind of thing a microcontroller does all day:
clean up a noisy button, scale an ADC reading, buffer UART bytes, filter a sensor,
drive a motor. You can solve them in any language, but they are written with
**ESPresso** in mind, the small scripting language built for the ESP32. This lesson
is a tour of ESPresso and of the integer-first habits embedded code depends on.

## Two engines, one language

ESPresso source goes through a classic pipeline:

```text
source ──► lexer ──► parser ──► AST ──┬──► compiler ──► bytecode ──► stack VM   (default)
                                      └──► tree-walking interpreter            (--interp)
```

The **bytecode VM** is the default: the AST is compiled once into compact opcodes
(`OP_ADD`, `OP_GET_LOCAL`, `OP_LOOP`…) that a tight `switch` loop executes. The
**AST interpreter** (`ESPresso --interp file.espr`) walks the tree directly. It is
slower but simpler, which makes it handy for checking the VM. Both run the same
programs; Crucible uses the VM.

The VM is small on purpose, and the limits come from fixed-size tables:
about **64 call frames** (so recursion only goes ~60 deep), at most **256
constants per chunk**, and **64 variables per environment**. On a chip with
520 KB of RAM, fixed tables you can reason about beat a heap that might fragment.

## Syntax tour

```espresso
// line comments only (no /* block */ comments)
var count = 0              // mutable
const LIMIT = 100          // meant to stay constant
var ratio = 0.5            // float (32-bit!)
var on = true              // bool
var buf = [0, 0, 0, 0]     // array literal: the size is fixed from now on
var pt = {x: 3, y: 4}      // object; pt.x, pt.y = 9

fn clamp(v, lo, hi) {      // functions: fn name(params) { ... }
    if v < lo { return lo } else if v > hi { return hi }
    return v
}

for var i in 0..len(buf) { // half-open range: 0, 1, 2, 3
    buf[i] = i * i
}
while count < 3 { count += 1 }    // += -= *= /= all work, also on buf[i]
print("count is {count}")         // {expr} interpolation inside strings
```

No semicolons, no parentheses around conditions, and braces are always required.
Logical operators are `and`, `or`, `!`. (`&&` and `||` also exist, but they currently break
inside a function call's arguments, so stick to the words.)

Functions are first-class, and inner functions capture their surroundings. Closures
are the ESPresso way to keep state alive between calls, much like a `static`
local in C:

```espresso
fn makeCounter() {
    var n = 0
    fn tick() {
        n += 1
        return n
    }
    return tick
}
var c = makeCounter()
c()
c()            // returns 2: n survived between calls
```

Arrays and objects are passed to functions **by reference**, so a function can fill
a caller's buffer in place. (Careful: `var b = a` at the top level of a script
*copies* the array, while inside a function it aliases. Mutate through parameters
and don't depend on either behaviour.)

## The quirks, and the idioms that get around them

| Missing / different | Idiom |
|---|---|
| no `%` operator | `a - (a / b) * b` (same sign rules as C's `%`) |
| no `& \| ^ << >>` | `x / 2` is a right shift for x ≥ 0, `x * 2` a left shift; the low bit is `x - (x / 2) * 2` |
| ints are **32-bit** and wrap silently | keep products under 2³¹ ≈ 2.1·10⁹; split or rescale before multiplying |
| `/` on two ints **truncates toward zero** | `-7 / 2` is `-3` (C semantics, unlike Python's `-4`) |
| `int / int` stays an int | start float accumulators at `0.0` so the division is float |
| arrays never grow (no push, no concat) | allocate a fixed buffer up front, track a `count` |
| strings cannot be indexed | work with arrays of codes instead |
| recursion is ~60 frames deep | write loops; keep recursion for tiny depths |
| no `min`, `max`, `abs` built-ins | three-line helper functions |

The modulo idiom shows up constantly, so it is worth seeing why it works. Integer
division throws away the remainder: `17 / 5` is `3`, so `(17 / 5) * 5` is `15`, and
`17 - 15` gives back the `2` that was dropped. For ring buffers you usually don't
even need that: you advance an index by one at a time, so a compare does the job:

```espresso
idx += 1
if idx == capacity { idx = 0 }   // wrap without dividing
```

On a real MCU this is also faster: many small cores have no hardware divider, and a
software divide costs dozens of cycles.

## Why embedded code loves integers

An ESP32 has a floating-point unit, but plenty of microcontrollers don't (the ESP8266,
Cortex-M0, AVR). On those, every `float` operation is a library call costing
tens to hundreds of cycles. Even with an FPU, floats raise their own questions:
how does `0.1 + 0.2` round, and will two builds agree on the answer bit for bit?
Integer math is exact, deterministic and cheap, so firmware uses it wherever it can:

- **Scale instead of using fractions.** A temperature of 23.57 °C is stored as `2357`
  centi-degrees. Percentages become per-mille. Sensors already deliver integers
  (a 10-bit ADC gives 0–1023).
- **Fixed point.** Choose an implied binary point: in **Q8** format the integer
  `384` means `384 / 256 = 1.5`. Adding two Q8 numbers is plain addition.
  Multiplying gives a Q16 result, so you divide by 256 to get back to Q8, and
  that is where rounding and overflow decisions live.
- **Say how you round.** Truncate toward zero (what C and ESPresso `/` do), floor, or
  round half away from zero (`(x + 128) / 256` for non-negative `x`)? Every
  problem here states its rule. When you port the code, match it exactly.
- **Saturate, don't wrap.** When a result leaves its range, clamp it to the limit. A motor
  command that wraps from +32767 to −32768 slams the motor into reverse.

ESPresso's floats are 32-bit (`float`, not `double`) and print with 6 significant
digits, which is another reason the problems here favour integer outputs.

## How Crucible runs your ESPresso

Your file is loaded, then one call per test is appended to it, and the whole thing
runs in a single VM:

```espresso
fn mapRange(x, inMin, inMax, outMin, outMax) { ... }   // your code
print("@@CRUCIBLE", 0, mapRange(512, 0, 1023, 0, 255))
print("@@CRUCIBLE", 1, mapRange(1023, 0, 1023, 0, 255))
```

Function and parameter names are camelCase (`map_range` → `mapRange`). Arrays arrive
as literals and are passed by reference. For "modify in place" problems the harness
prints the array after your function returns. Return ints as ints. If you return
`3.0` where `3` is expected, it still compares equal.

## The patterns in this track

| Problem | Embedded idea |
|---|---|
| Map a Sensor Range, Joystick Deadband | integer scaling, truncation, clamping |
| Intel HEX Checksum | byte arithmetic mod 256, two's complement |
| Schmitt Trigger, Button Debounce | state machines over a sample stream |
| Integer Square Root | binary search that can't overflow 32 bits |
| Moving Average Peak | sliding-window sums |
| UART Ring Buffer | fixed-capacity FIFO with wrap-around indices |
| BCD Counter | digit packing without bit operators |
| Blinking LEDs | per-LED state kept in closures |
| Fixed-Point FIR Filter | Q8 multiply-accumulate, rounding, saturation, in-place |
| PID Motor Controller | integer PID with anti-windup and output limits |
""",
)


# ESPresso compiles the whole harness (your code + one line per test) into a single chunk
# that holds at most 256 constants, and every literal counts. Keep each problem's tests
# inside that budget so the ESPresso run can't fail for reasons unrelated to the solution.
def _leaves(v):
    return sum(_leaves(x) for x in v) if isinstance(v, list) else 1


def _esp_budget(p):
    per_test = 9 if p.get("mutates") else 5
    used = 10 + sum(per_test + _leaves(t) for t in p["tests"])
    assert used <= 245, f"{p['id']}: ESPresso constant budget {used} > 245"


_rng = random.Random(1818)

PROBLEMS = []

# ---------------------------------------------------------------- 1. map range
PROBLEMS.append(dict(
    id="map-sensor-range",
    title="Map a Sensor Range",
    difficulty=1,
    tags=["math", "integer division", "embedded"],
    fn="map_range",
    params=[["x", "int"], ["in_min", "int"], ["in_max", "int"], ["out_min", "int"], ["out_max", "int"]],
    returns="int",
    statement=r"""
A potentiometer is wired to a 10-bit ADC, so `analogRead()` returns `0…1023`. The PWM
peripheral wants `0…255`. Arduino's famous `map()` converts between ranges with
integer math only:

```c
long map(long x, long in_min, long in_max, long out_min, long out_max) {
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
```

Implement `map_range(x, in_min, in_max, out_min, out_max)` with **exactly** this
behaviour:

- Compute `(x - in_min) * (out_max - out_min)` and divide it by `(in_max - in_min)`
  using **C integer division, which truncates toward zero** (`-7 / 2 == -3`).
- Add `out_min`.
- Do **not** clamp: `x` may lie outside `[in_min, in_max]`, and either range may be
  "reversed" (`out_min > out_max` or `in_min > in_max`).
""",
    constraints=["`in_min ≠ in_max`", "`|(x - in_min) · (out_max - out_min)| < 2³¹`", "all values fit in 32-bit signed ints"],
    example_notes=[
        "`512 · 255 / 1023 = 130560 / 1023 = 127.6…`, truncated to `127`. Integer `map()` never rounds up.",
        "The full-scale reading maps exactly to the top of the output range.",
    ],
    hints=[
        "This is one line in C. The work is matching the rounding rule in your language.",
        "Truncation toward zero only differs from flooring when the quotient is negative. That happens with reversed ranges.",
        "In Python, `//` floors. Divide the absolute values, then put the sign back: negative when exactly one operand is negative.",
    ],
    solution=r'''def map_range(x, in_min, in_max, out_min, out_max):
    # Arduino's map() is pure integer math. The only subtle part is the division:
    # C (and ESPresso) truncate toward zero, but Python's // floors toward -infinity.
    num = (x - in_min) * (out_max - out_min)
    den = in_max - in_min

    # Divide the magnitudes (always non-negative, so floor == truncate here)...
    q = abs(num) // abs(den)
    # ...then restore the sign: negative exactly when the operands' signs differ.
    if (num < 0) != (den < 0):
        q = -q

    # Shift into the output range. No clamping: out-of-range inputs extrapolate.
    return q + out_min
''',
    refs={
        "espresso": r'''// Arduino map(): ESPresso's "/" already truncates toward zero, exactly like
// C's long division, so the formula ports over unchanged.
fn mapRange(x, inMin, inMax, outMin, outMax) {
    var num = (x - inMin) * (outMax - outMin)   // stays < 2^31 by the constraints
    return num / (inMax - inMin) + outMin        // truncating divide, then shift
}
''',
        "cpp": r'''// C++ integer division truncates toward zero, the same as Arduino's C.
long long mapRange(long long x, long long in_min, long long in_max, long long out_min, long long out_max) {
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
''',
        "rust": r'''// Rust's `/` on integers also truncates toward zero.
pub fn map_range(x: i64, in_min: i64, in_max: i64, out_min: i64, out_max: i64) -> i64 {
    (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
}
''',
    },
    explanation=r"""
## Intuition

Mapping one range onto another is a straight line: slide the input so `in_min` sits at 0,
stretch by the ratio of the range widths, slide to `out_min`. With real numbers that is

```text
y = (x - in_min) · (out_max - out_min) / (in_max - in_min) + out_min
```

Firmware does it in integers. **Multiply first, then divide**, so the fraction is never
lost early: `512 / 1023 * 255` would be `0 * 255 = 0` in integer math, while
`512 * 255 / 1023` is `127`.

## Approach

1. `num = (x - in_min) * (out_max - out_min)`
2. `den = in_max - in_min`
3. `q = num / den` with truncation toward zero
4. return `q + out_min`

Trace for a reversed output range, `map(300, 0, 1023, 255, 0)`:

| step | value |
|---|---|
| num | `300 · (0 − 255) = −76500` |
| den | `1023` |
| exact quotient | `−74.78…` |
| truncate toward 0 | `−74` |
| + out_min | `−74 + 255 = 181` |

A floor division gives `−75` and then `180`, one off. Matching the original C
code means matching its rounding.

## Complexity

O(1) time and space.

## Common mistakes

- **Using Python's `//`.** It floors, so negative quotients come out one too small. Divide
  magnitudes and reapply the sign, or use `int(num / den)` (safe here because the values are
  far below 2⁵³).
- **Dividing before multiplying.** `(x - in_min) / (in_max - in_min)` is 0 for every
  in-range input.
- **Overflow.** On an 8-bit AVR, `int` is 16 bits; Arduino's `map()` uses `long`
  (32 bits) for exactly this reason. In ESPresso ints are 32-bit, so
  `(x - in_min) · (out_max - out_min)` must stay below 2³¹. Mapping a 24-bit ADC onto
  a 16-bit range would overflow.
- **Clamping.** The real `map()` doesn't clamp, and neither should you here. Real firmware
  often wraps it as `constrain(map(...), lo, hi)`.

## Going further

`map()` is biased: only an input of exactly 1023 reaches 255, so the top output bucket is one
count wide. A better-distributed version maps `x * (out_span + 1) / (in_span + 1)`. Try
both on all 1024 inputs and count how many inputs land on each output.
""",
    tests=[
        [512, 0, 1023, 0, 255],
        [1023, 0, 1023, 0, 255],
        [0, 0, 1023, 0, 255],
        [300, 0, 1023, 255, 0],
        [50, 0, 100, -100, 100],
        [-10, 0, 100, 0, 1000],
        [700, 1000, 0, 0, 100],
        [3, 0, 7, 0, 9],
        [2047, 0, 4095, -400, 1250],
        [1, 0, 3, 10, 0],
        [1500, 0, 1023, 0, 255],
        [-5, -10, 10, 1000, 2000],
    ],
))

# ---------------------------------------------------------------- 2. joystick deadband
PROBLEMS.append(dict(
    id="joystick-deadband",
    title="Joystick Deadband",
    difficulty=1,
    tags=["math", "clamp", "embedded"],
    fn="joystick_axis",
    params=[["raw", "int"], ["center", "int"], ["deadband", "int"], ["limit", "int"]],
    returns="int",
    statement=r"""
A cheap analog joystick never rests exactly at its center: at rest it drifts a few
counts either side. To stop the robot creeping, firmware applies a **deadband** around
the center and then **clamps** the result to what the motor driver accepts.

Implement `joystick_axis(raw, center, deadband, limit)`:

1. `offset = raw - center`
2. If `|offset| ≤ deadband`, the stick is "at rest": return `0`.
3. Otherwise move `offset` toward zero by `deadband` (so the output starts at ±1 just
   outside the band instead of jumping to ±(deadband + 1)).
4. Clamp the result to `[-limit, limit]` and return it.
""",
    constraints=["`0 ≤ deadband`", "`0 ≤ limit`", "values fit in 32-bit signed ints"],
    example_notes=[
        "Dead center gives `0`.",
        "`offset = 18 ≤ 20`: still inside the deadband, so `0`.",
    ],
    hints=[
        "Handle the three regions separately: inside the band, above it, below it.",
        "Above: `offset - deadband`. Below: `offset + deadband`.",
        "Clamp last: `max(-limit, min(limit, value))`.",
    ],
    solution=r'''def joystick_axis(raw, center, deadband, limit):
    offset = raw - center

    # Inside the deadband (inclusive) the stick counts as centred.
    if -deadband <= offset <= deadband:
        return 0

    # Outside it, remove the band so the response starts smoothly at +/-1
    # instead of jumping straight to +/-(deadband + 1).
    if offset > 0:
        value = offset - deadband
    else:
        value = offset + deadband

    # Saturate to what the motor driver accepts.
    return max(-limit, min(limit, value))
''',
    refs={
        "espresso": r'''// Deadband then clamp. ESPresso has no abs/min/max, so compare explicitly.
fn joystickAxis(raw, center, deadband, limit) {
    var offset = raw - center
    if offset >= -deadband and offset <= deadband {
        return 0                        // inside the band: at rest
    }
    var value = offset + deadband       // assume below the band...
    if offset > 0 {
        value = offset - deadband       // ...unless above it
    }
    if value > limit { return limit }   // saturate high
    if value < -limit { return -limit } // saturate low
    return value
}
''',
        "cpp": r'''// Deadband, shrink toward zero, then std::clamp.
long long joystickAxis(long long raw, long long center, long long deadband, long long limit) {
    long long off = raw - center;
    if (off >= -deadband && off <= deadband) return 0;
    long long v = off > 0 ? off - deadband : off + deadband;
    return clamp(v, -limit, limit);
}
''',
        "rust": r'''// i64::clamp saturates into [-limit, limit].
pub fn joystick_axis(raw: i64, center: i64, deadband: i64, limit: i64) -> i64 {
    let off = raw - center;
    if off.abs() <= deadband {
        return 0;
    }
    let v = if off > 0 { off - deadband } else { off + deadband };
    v.clamp(-limit, limit)
}
''',
    },
    explanation=r"""
## Intuition

Plot output against offset and you get three pieces: a flat zero section of width
`2·deadband + 1` in the middle, then two sloped lines that start at ±1, then flat
again at ±limit. Each piece is one `if`.

```text
 output
  +limit ┤                 ┌──────
         │               ╱
         │             ╱
       0 ┤ ───────┬───┼───┬──
         │      ╱ -db 0  +db
         │    ╱
  -limit ┤───┘
```

## Approach

1. `offset = raw - center`.
2. `|offset| ≤ deadband` → `0`.
3. Subtract the deadband from the magnitude, keeping the sign.
4. Clamp.

Trace `joystick_axis(1023, 512, 20, 400)`: offset `511`, minus deadband gives `491`,
clamped to `400`.

## Complexity

O(1).

## Common mistakes

- **Strict vs inclusive bounds.** The spec says `|offset| ≤ deadband` is at rest, so an
  offset of exactly 20 with deadband 20 gives 0, and 21 gives 1.
- **Forgetting to shrink.** Returning `offset` itself would jump from 0 to 21 as the stick
  crosses the edge, a jerk the robot feels.
- **Clamping only one side.** Negative offsets need clamping too.
- **ESPresso:** there's no `abs()`, so either write the two-sided comparison as in the reference
  or define a tiny `fn abs(x)`.

## Going further

Joysticks are rarely symmetric: one side of the pot may reach 1023 while the other only
gets to 40. Calibrated firmware stores `min`, `center`, `max` per axis and maps each half
separately with `map()` (previous problem), so both directions reach full scale.
""",
    tests=[
        [512, 512, 20, 400],
        [530, 512, 20, 400],
        [533, 512, 20, 400],
        [1023, 512, 20, 400],
        [0, 512, 20, 400],
        [490, 512, 20, 400],
        [532, 512, 20, 400],
        [100, 0, 0, 50],
        [-7, 0, 0, 100],
        [2048, 2048, 0, 10],
        [470, 512, 20, 400],
        [600, 512, 20, 0],
    ],
))

# ---------------------------------------------------------------- 3. checksum
_hex_tests = [
    [[0x03, 0x00, 0x30, 0x00, 0x02, 0x33, 0x7A]],
    [[0x10, 0x01, 0x00, 0x00, 0x21, 0x46, 0x01, 0x36, 0x01, 0x21, 0x47, 0x01, 0x36, 0x00, 0x7E, 0xFE, 0x09, 0xD2, 0x19, 0x01]],
    [[0x00, 0x00, 0x00, 0x01]],
    [[]],
    [[0]],
    [[255]],
    [[128, 128]],
    [[0x02, 0x00, 0x00, 0x04, 0xFF, 0xFF]],
]
for _n in (12, 16):
    _hex_tests.append([[_rng.randint(0, 255) for _ in range(_n)]])
PROBLEMS.append(dict(
    id="intel-hex-checksum",
    title="Intel HEX Checksum",
    difficulty=1,
    tags=["math", "modulo", "embedded"],
    fn="hex_checksum",
    params=[["record", "int[]"]],
    returns="int",
    statement=r"""
Firmware images are often shipped as **Intel HEX** files, lines like
`:0300300002337A1E`. After the colon, each pair of hex digits is one byte, and the
**last byte is a checksum**: it is chosen so that all the bytes of the line,
checksum included, add up to `0` modulo 256.

Given the bytes of a record **without** its checksum (`record[i]` in `0…255`),
return the checksum byte:

```text
checksum = (256 − (sum of bytes mod 256)) mod 256
```

That is the two's complement of the low byte of the sum. An empty record has checksum `0`.
""",
    constraints=["`0 ≤ len(record) ≤ 32`", "`0 ≤ record[i] ≤ 255`"],
    example_notes=[
        "The bytes of `:0300300002337A1E` are `03 00 30 00 02 33 7A`. They sum to `0xE2 = 226`, and `256 − 226 = 30 = 0x1E`, the `1E` at the end of the line.",
        "The second line from the Intel HEX spec, `…0140`: the checksum is `0x40 = 64`.",
    ],
    hints=[
        "Add up the bytes, then keep only the low 8 bits (mod 256).",
        "The checksum is `256 - low`, except that when `low` is 0 the answer must be 0, not 256.",
        "Without `%`: after each addition, if the running sum reaches 256, subtract 256. A `uint8_t` accumulator does exactly that.",
    ],
    solution=r'''def hex_checksum(record):
    # Sum every byte; only the low 8 bits matter, exactly like adding into a uint8_t.
    low = sum(record) % 256

    # Two's complement of that byte: the value that brings the total back to 0 mod 256.
    # The outer % 256 turns "256" (when low == 0) into 0, keeping the result a byte.
    return (256 - low) % 256
''',
    refs={
        "espresso": r'''// ESPresso has no % operator. Instead, mimic a uint8_t accumulator: after each
// add, fold the sum back into 0..255. Each byte is <= 255, so one subtraction suffices.
fn hexChecksum(record) {
    var sum = 0
    for var i in 0..len(record) {
        sum += record[i]
        if sum >= 256 { sum -= 256 }
    }
    if sum == 0 { return 0 }   // 256 - 0 would be 256, which isn't a byte
    return 256 - sum
}
''',
        "cpp": r'''// Let an unsigned 8-bit type do the wrap-around for us.
long long hexChecksum(vector<long long>& record) {
    uint8_t sum = 0;
    for (long long b : record) sum += (uint8_t)b;   // wraps mod 256
    return (uint8_t)(0 - sum);                       // two's complement, still a byte
}
''',
        "rust": r'''// u8 wrapping arithmetic models the firmware accumulator exactly.
pub fn hex_checksum(record: Vec<i64>) -> i64 {
    let sum = record.iter().fold(0u8, |acc, &b| acc.wrapping_add(b as u8));
    sum.wrapping_neg() as i64
}
''',
    },
    explanation=r"""
## Intuition

A checksum is a cheap way to catch corrupted bytes. The receiver adds up the whole line,
checksum included, and expects 0 (mod 256). So the sender needs the number that
**cancels** the low byte of the sum. In 8-bit arithmetic that's the negation:
`−s mod 256`, i.e. `256 − s` (or `0` when `s = 0`).

## Approach

Trace `03 00 30 00 02 33 7A`:

| byte | running sum (mod 256) |
|---|---|
| 0x03 | 3 |
| 0x00 | 3 |
| 0x30 | 51 |
| 0x00 | 51 |
| 0x02 | 53 |
| 0x33 | 104 |
| 0x7A | 226 |

`256 − 226 = 30 = 0x1E`. Check: `226 + 30 = 256 ≡ 0`.

Reducing mod 256 **as you go** gives the same answer as reducing at the end, because
`(a + b) mod m = ((a mod m) + b) mod m`. Firmware does it as it goes because its
accumulator is a single byte; in ESPresso it also keeps the sum small.

## Complexity

O(n) time, O(1) space.

## Common mistakes

- **Returning 256.** When the low byte is already 0 the checksum is 0. `256 − 0` is not a byte.
- **Bitwise NOT instead of negate.** `~s` is the *one's* complement (`255 − s`); Intel HEX
  uses the two's complement (`256 − s`). They differ by exactly one.
- **Python's negative `%`** is fine here (`-226 % 256 == 30`), but C's `%` would give `-226`.
  Always reason about the sign rules of your language's remainder.

## Going further

A sum can't detect two bytes swapped in place. CRCs (CRC-8, CRC-16/CCITT) treat the data as
a polynomial and catch swaps and burst errors; they are the next step for any serious
link. Without bit operators, an ESPresso CRC needs `x / 2` for shifts and the manual-modulo
idiom for the low bit.
""",
    tests=_hex_tests,
))

# ---------------------------------------------------------------- 4. schmitt trigger
_sch_tests = [
    [[0, 30, 55, 70, 65, 50, 40, 20, 35, 61, 80], 30, 60],
    [[10, 59, 59, 61, 59, 61, 31, 29, 60], 30, 60],
    [[100, 100, 100], 30, 60],
    [[], 10, 20],
    [[5, 25, 5, 25, 5, 25], 5, 25],
    [[50, 40, 50, 40, 50], 30, 60],
]
for _ in range(2):
    _v, _sig = 500, []
    for _ in range(24):
        _v = max(0, min(1023, _v + _rng.randint(-160, 160)))
        _sig.append(_v)
    _sch_tests.append([_sig, 400, 600])
PROBLEMS.append(dict(
    id="schmitt-trigger",
    title="Schmitt Trigger",
    difficulty=1,
    tags=["state machine", "simulation", "embedded"],
    fn="schmitt_edges",
    params=[["signal", "int[]"], ["low", "int"], ["high", "int"]],
    returns="int",
    statement=r"""
A light sensor hovering around a single threshold would make a "lights on" output
flicker hundreds of times a second. A **Schmitt trigger** fixes that with **two**
thresholds (hysteresis):

- The output starts **low**.
- While low, it switches **high** as soon as a sample is `≥ high`.
- While high, it switches back **low** as soon as a sample is `≤ low`.
- Anything strictly between `low` and `high` leaves the output unchanged.

Return the number of **rising edges** (low → high transitions) over the samples in
`signal`.
""",
    constraints=["`0 ≤ len(signal) ≤ 100`", "`low < high`"],
    example_notes=[
        "Rises at 70, falls at 20, rises again at 61: two rising edges. The dip to 40 in between is above `low = 30`, so it doesn't reset the output.",
        "The noisy `59/61/59/61` near the top threshold produces only one edge, because the output can't fall again until a sample reaches 30. It falls at `29`, and the final `60` is the second rise.",
    ],
    hints=[
        "Keep one boolean, the current output, and look at each sample once.",
        "Which threshold you compare against depends on the current state.",
        "Count only the low → high switches.",
    ],
    solution=r'''def schmitt_edges(signal, low, high):
    output_high = False   # the trigger powers up with its output low
    edges = 0

    for v in signal:
        if not output_high and v >= high:
            # Only the upper threshold can switch us on...
            output_high = True
            edges += 1
        elif output_high and v <= low:
            # ...and only the lower threshold can switch us off.
            output_high = False
        # Samples in between: hysteresis keeps the current state.

    return edges
''',
    refs={
        "espresso": r'''// A two-state machine. The threshold we test depends on the current state.
fn schmittEdges(signal, low, high) {
    var outHigh = false
    var edges = 0
    for var i in 0..len(signal) {
        var v = signal[i]
        if !outHigh and v >= high {
            outHigh = true      // rising edge
            edges += 1
        } else if outHigh and v <= low {
            outHigh = false     // falling edge
        }
    }
    return edges
}
''',
        "cpp": r'''// Same state machine; `hi` is the output state.
long long schmittEdges(vector<long long>& signal, long long low, long long high) {
    bool hi = false;
    long long edges = 0;
    for (long long v : signal) {
        if (!hi && v >= high) { hi = true; edges++; }
        else if (hi && v <= low) hi = false;
    }
    return edges;
}
''',
        "rust": r'''pub fn schmitt_edges(signal: Vec<i64>, low: i64, high: i64) -> i64 {
    let mut hi = false;
    let mut edges = 0;
    for v in signal {
        if !hi && v >= high {
            hi = true;
            edges += 1;
        } else if hi && v <= low {
            hi = false;
        }
    }
    edges
}
''',
    },
    explanation=r"""
## Intuition

One threshold has no memory: a signal hovering at the threshold crosses it on every
bit of noise. Two thresholds give the output a **memory**: once it is high, the
signal must drop a long way, past `low`, before it turns off. This is your first
**state machine**: the output depends on the input *and* on the current state.

```text
 high ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
              /\/\/\        noise near "high" can't toggle us
 low  ─ ─ ─ ─/─ ─ ─ \─ ─ ─ ─
  output: ___┌───────┐______
```

## Approach

| state | sample | action |
|---|---|---|
| low | `≥ high` | go high, count an edge |
| low | otherwise | stay low |
| high | `≤ low` | go low |
| high | otherwise | stay high |

Trace example 1 (`low = 30`, `high = 60`):

| sample | 0 | 30 | 55 | **70** | 65 | 50 | 40 | **20** | 35 | **61** | 80 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| state | L | L | L | H | H | H | H | L | L | H | H |

Two rising edges.

## Complexity

O(n) time, O(1) space.

## Common mistakes

- **Testing both thresholds regardless of state**, e.g. `if v >= high: …` followed by a
  separate `if v <= low: …`. It happens to work here, but stating the state explicitly is clearer
  and extends to more states.
- **Strict vs inclusive comparisons.** The spec says `≥ high` and `≤ low`; the test with
  samples exactly at the thresholds checks that.
- **Counting falling edges too.**

## Going further

Hardware Schmitt triggers (the 74HC14, or the input buffers inside most MCUs) do this in
silicon. In software the same pattern drives thermostats: heat on below 19.5 °C, off above
20.5 °C, so the relay doesn't chatter. Try returning the number of samples spent high, or the
length of the longest high pulse.
""",
    tests=_sch_tests,
))

# ---------------------------------------------------------------- 5. isqrt
PROBLEMS.append(dict(
    id="integer-square-root",
    title="Integer Square Root",
    difficulty=2,
    tags=["binary search", "math", "overflow"],
    fn="isqrt",
    params=[["n", "int"]],
    returns="int",
    statement=r"""
An accelerometer reports `x`, `y`, `z` in milli-g, and you need the magnitude
`√(x² + y² + z²)`. There is no FPU, so you need an **integer square root**.

Return `⌊√n⌋`, the largest integer `r` with `r · r ≤ n`.

The catch: your target uses **32-bit signed integers**. `n` comes from a 24-bit sensor
pipeline (below `2²⁴`), but any intermediate value you compute must stay below `2³¹`
(ESPresso wraps silently; C would invoke undefined behaviour). A binary search that starts
with `hi = n` squares numbers in the millions and overflows.
""",
    constraints=["`0 ≤ n < 2²⁴ = 16 777 216`", "every intermediate value must fit in a 32-bit signed int"],
    example_notes=[
        "`4 · 4 = 16 ≤ 17 < 25`, so the answer is 4.",
        "`4000² = 16 000 000` exactly. Squaring the naive first midpoint, `8 million`, would overflow 32 bits.",
    ],
    examples=2,
    hints=[
        "The answer is monotonic in `r` (`r² ≤ n` holds up to some point, then fails forever), so binary search applies.",
        "The root of any 32-bit value is at most `46340`, because `46341²` already exceeds `2³¹ − 1`. So `hi = min(n, 46340)` keeps every `mid * mid` in range.",
        "Search `lo = 0, hi = 46340`. With `mid = (lo + hi + 1) / 2`: if `mid * mid <= n`, set `lo = mid`, else `hi = mid - 1`.",
    ],
    solution=r'''def isqrt(n):
    # Binary search for the largest r with r*r <= n.
    # Upper bound 46340: 46341^2 > 2^31 - 1, so a 32-bit target never squares
    # anything that could overflow.
    lo, hi = 0, min(n, 46340)
    while lo < hi:
        # Round the midpoint UP: with lo = mid on success, rounding down
        # could leave lo == mid forever (infinite loop when hi == lo + 1).
        mid = (lo + hi + 1) // 2
        if mid * mid <= n:
            lo = mid        # mid works; the answer is mid or larger
        else:
            hi = mid - 1    # mid is too big; the answer is below it
    return lo
''',
    refs={
        "espresso": r'''// Binary search on the answer. hi starts at 46340 so mid * mid can never
// exceed 46340^2 = 2147395600 < 2^31: no silent 32-bit wraparound.
fn isqrt(n) {
    var lo = 0
    var hi = 46340
    if n < hi { hi = n }
    while lo < hi {
        var mid = (lo + hi + 1) / 2     // round up so "lo = mid" always makes progress
        if mid * mid <= n {
            lo = mid
        } else {
            hi = mid - 1
        }
    }
    return lo
}
''',
        "cpp": r'''// Same search, written with the 32-bit-safe comparison mid <= n / mid.
long long isqrt(long long n) {
    long long lo = 0, hi = min(n, 46340LL);
    while (lo < hi) {
        long long mid = (lo + hi + 1) / 2;
        if (mid <= n / mid) lo = mid; else hi = mid - 1;
    }
    return lo;
}
''',
        "rust": r'''pub fn isqrt(n: i64) -> i64 {
    let (mut lo, mut hi) = (0i64, n.min(46340));
    while lo < hi {
        let mid = (lo + hi + 1) / 2;
        if mid * mid <= n { lo = mid } else { hi = mid - 1 }
    }
    lo
}
''',
    },
    explanation=r"""
## Intuition

`f(r) = (r² ≤ n)` is `true, true, …, true, false, false, …`, and we want the last `true`.
Whenever a yes/no predicate flips exactly once, **binary search on the answer** finds the
flip in O(log range) steps.

The embedded twist is **overflow**. If you set `hi = n` with `n = 16 000 000`, the first midpoint is
8 million, and its square (6.4·10¹³) wraps around in 32 bits into garbage, possibly
negative, which then looks `≤ n`. The fix: the root of *any* 32-bit value is at most
`46340`, so search only there. That bound works unchanged even for `n = 2³¹ − 1`.

## Approach

```text
lo = 0, hi = min(n, 46340)
while lo < hi:
    mid = (lo + hi + 1) / 2        // upper middle
    if mid*mid <= n: lo = mid
    else:            hi = mid - 1
return lo
```

Trace `n = 17`:

| lo | hi | mid | mid² ≤ 17? |
|---|---|---|---|
| 0 | 17 | 9 | 81 no → hi = 8 |
| 0 | 8 | 4 | 16 yes → lo = 4 |
| 4 | 8 | 6 | 36 no → hi = 5 |
| 4 | 5 | 5 | 25 no → hi = 4 |

`lo = hi = 4`.

**Why the upper middle?** When `hi = lo + 1`, the lower middle is `lo`. If it succeeds,
`lo = mid` changes nothing and the loop spins forever. Rounding up guarantees progress.

## Complexity

O(log 46340) ≈ 16 iterations, O(1) space.

## Common mistakes

- `hi = n` and squaring huge midpoints: overflow in 32 bits.
- Lower-middle midpoint with `lo = mid`: infinite loop.
- Using floating point (`int(math.sqrt(n))`). Fine in Python with doubles, but with
  32-bit floats (ESPresso, many MCUs) `2147395599` itself isn't representable, and its root
  comes out as `46340.0`, one too high. (Here n < 2²⁴ would be safe, but the habit isn't.)
- `mid <= n / mid` (as in the C++ reference) is another overflow-proof test; just
  guard `mid = 0`.

## Going further

Newton's method, `r = (r + n / r) / 2`, converges quadratically (about 5 steps from a good
start). There is also a classic digit-by-digit "shift-and-subtract" root that uses only
shifts and adds, ideal for cores without a hardware multiplier.
""",
    tests=[[17], [16000000], [0], [1], [2], [3], [4], [15], [16], [99], [1000000], [16769025], [16769024], [16777215], [65535]],
))

# ---------------------------------------------------------------- 6. debounce
def _bouncy(rng, presses, k):
    """A realistic button trace: idle, bounce, held, bounce, released."""
    out = [0] * rng.randint(0, 2)
    for _ in range(presses):
        out += [rng.randint(0, 1) for _ in range(rng.randint(0, 3))]   # contact bounce
        out += [1] * rng.randint(1, k + 2)                              # held (maybe too short)
        out += [rng.randint(0, 1) for _ in range(rng.randint(0, 3))]
        out += [0] * rng.randint(1, k + 2)
    return out


_deb_tests = [
    [[0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0], 3],
    [[1, 1, 0, 1, 1, 0, 1, 1], 3],
    [[1], 1],
    [[], 4],
    [[1, 0, 1, 0, 1, 0], 1],
    [[1, 1, 1, 1, 1, 1, 1, 1], 8],
]
for _k in (2, 3, 4):
    _deb_tests.append([_bouncy(_rng, 3, _k)[:28], _k])
PROBLEMS.append(dict(
    id="button-debounce",
    title="Button Debounce",
    difficulty=2,
    tags=["state machine", "simulation", "embedded"],
    fn="count_presses",
    params=[["samples", "int[]"], ["k", "int"]],
    returns="int",
    statement=r"""
Mechanical button contacts **bounce**: for a few milliseconds after a press, the
GPIO reads `1, 0, 1, 1, 0, 1…` before settling. Firmware samples the pin on a timer
tick and keeps a **debounced state** that only changes once the raw input has
disagreed with it for `k` **consecutive** samples.

Simulate the debouncer over `samples` (each `0` = released, `1` = pressed):

- The debounced state starts at `0` (released), with a disagreement counter of `0`.
- For each sample:
  - if it equals the debounced state, reset the counter to `0`;
  - otherwise increment the counter, and if it reaches `k`, flip the debounced state
    and reset the counter to `0`.

Return the number of times the debounced state flips from `0` to `1` (clean presses).
""",
    constraints=["`0 ≤ len(samples) ≤ 100`", "`samples[i] ∈ {0, 1}`", "`1 ≤ k ≤ 10`"],
    example_notes=[
        "The single `1` at index 1 is a glitch (counter 1, then reset). Indices 3–5 are three 1s in a row, so the state flips to pressed at index 5. The lone 0 at index 7 doesn't release it; the four 0s at the end do (after the third). One press.",
        "The 0s interrupt each run of 1s before the counter reaches 3, so the state never flips.",
    ],
    hints=[
        "You need two variables besides the answer: the debounced state and the run counter.",
        "A sample that agrees with the state must reset the counter. That's what makes the k samples *consecutive*.",
        "Count a press only when the state flips to 1, not when it flips back to 0.",
    ],
    solution=r'''def count_presses(samples, k):
    state = 0      # debounced (trusted) button state: start released
    run = 0        # how many consecutive samples have disagreed with `state`
    presses = 0

    for s in samples:
        if s == state:
            # The input agrees with what we believe: any bounce streak is over.
            run = 0
        else:
            run += 1
            if run == k:
                # k disagreeing samples in a row: the change is real.
                state = s
                run = 0
                if state == 1:
                    presses += 1   # count only released -> pressed
    return presses
''',
    refs={
        "espresso": r'''// Counter-based debouncer, the same logic you'd run in a 1 ms timer interrupt.
fn countPresses(samples, k) {
    var state = 0
    var run = 0
    var presses = 0
    for var i in 0..len(samples) {
        if samples[i] == state {
            run = 0                 // agreement resets the streak
        } else {
            run += 1
            if run == k {           // stable for k ticks: accept the new level
                state = samples[i]
                run = 0
                if state == 1 { presses += 1 }
            }
        }
    }
    return presses
}
''',
        "cpp": r'''long long countPresses(vector<long long>& samples, long long k) {
    long long state = 0, run = 0, presses = 0;
    for (long long s : samples) {
        if (s == state) { run = 0; continue; }
        if (++run == k) {
            state = s;
            run = 0;
            presses += state;   // +1 only on a 0 -> 1 flip
        }
    }
    return presses;
}
''',
        "rust": r'''pub fn count_presses(samples: Vec<i64>, k: i64) -> i64 {
    let (mut state, mut run, mut presses) = (0, 0, 0);
    for s in samples {
        if s == state {
            run = 0;
        } else {
            run += 1;
            if run == k {
                state = s;
                run = 0;
                presses += state;
            }
        }
    }
    presses
}
''',
    },
    explanation=r"""
## Intuition

The raw pin can't be trusted for a few ticks after any change, so keep a **trusted
copy** of the state and only overwrite it once the evidence is overwhelming: `k` samples
in a row that all disagree. A single agreeing sample is proof the change was a bounce,
so the streak restarts. This is the "integrating" or counter debouncer used in countless
keyboard and button drivers.

## Approach

Trace example 1, `k = 3`:

| i | sample | run | state | event |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | |
| 1 | 1 | 1 | 0 | |
| 2 | 0 | 0 | 0 | glitch rejected |
| 3 | 1 | 1 | 0 | |
| 4 | 1 | 2 | 0 | |
| 5 | 1 | 3→0 | **1** | press #1 |
| 6 | 1 | 0 | 1 | |
| 7 | 0 | 1 | 1 | |
| 8 | 1 | 0 | 1 | bounce on release ignored |
| 9–11 | 0 0 0 | 1, 2, 3→0 | **0** | released |
| 12 | 0 | 0 | 0 | |

## Complexity

O(n) time, O(1) space. On a microcontroller this costs a few instructions per tick, which
is why it beats "wait 20 ms with `delay()` after an edge" (that blocks the whole loop).

## Common mistakes

- **Not resetting the counter on agreement.** Then any `k` disagreeing samples, even
  scattered, would flip the state.
- **Comparing to the previous sample instead of the debounced state.** That counts how
  long the raw input has been stable, a different (also valid) debouncer, but not this spec.
- **Counting releases** as presses.
- **Forgetting to reset `run` after a flip**, so the next streak starts part-way.

## Going further

Jack Ganssle's classic article *A Guide to Debouncing* measures real switches: bounce of
1–6 ms is typical, but some bounce for over 100 ms. Another elegant debouncer shifts each
sample into a byte, `history = (history << 1) | pin`, and declares "pressed" when
`history == 0xFF`. In ESPresso, without shifts, that's `history * 2 + pin`, folded back
below 256 with the manual-modulo idiom.
""",
    tests=_deb_tests,
))

# ---------------------------------------------------------------- 7. moving average peak
def _halves(rng, n, lo=-200, hi=200):
    return [rng.randint(lo, hi) / 2 for _ in range(n)]


_ma_tests = [
    [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0], 2],
    [[20.5, 21.0, 35.5, 21.5, 22.0, 22.5, 23.0, 22.5], 4],
    [[-3.5, -1.0, -2.5], 1],
    [[7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0], 8],
    [[-10.0, -20.0, -30.0, -40.0], 2],
    [[0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5], 8],
]
for _n, _w in ((14, 4), (16, 8), (12, 2)):
    _ma_tests.append([_halves(_rng, _n), _w])
PROBLEMS.append(dict(
    id="moving-average-peak",
    title="Moving Average Peak",
    difficulty=2,
    tags=["sliding window", "array", "float", "embedded"],
    fn="peak_average",
    # Float results are normally excluded from ESPresso (it prints 6 significant digits).
    # Every expected value here is a multiple of 1/16 below 100, so it prints exactly.
    espresso=True,
    params=[["samples", "float[]"], ["window", "int"]],
    returns="float",
    statement=r"""
A temperature sensor is noisy, so the firmware smooths it with a **simple moving
average** (SMA): the mean of the last `window` samples. An over-temperature alarm
should trip on the **highest smoothed value**, not on a single spike.

Given the samples and a window size, return the **maximum** of the averages of every
run of `window` consecutive samples (only full windows count).

`window` is a power of two (cheap to divide by on an MCU), and every sample is a
multiple of `0.5` (the sensor's resolution).
""",
    constraints=["`1 ≤ window ≤ len(samples) ≤ 20`", "`window ∈ {1, 2, 4, 8}`", "`-100 ≤ samples[i] ≤ 100`, each a multiple of 0.5"],
    example_notes=[
        "Windows of 2: averages `1.5, 2.5, 3.5, 4.5, 5.5`; the peak is `5.5`.",
        "Window sums are `98.5, 100.0, 101.5, 89.0, 90.0`. The spike `35.5` lifts the first three, and the best is `101.5 / 4 = 25.375`.",
    ],
    hints=[
        "Recomputing each window's sum from scratch costs O(n·w). Can you update the previous window's sum instead?",
        "Sliding one step right adds `samples[i]` and drops `samples[i - window]`.",
        "Track the maximum **sum** and divide once at the end. In ESPresso, start the sum at `0.0` so the final division is a float division.",
    ],
    solution=r'''def peak_average(samples, window):
    # Sum of the first full window.
    s = sum(samples[:window])
    best = s

    # Slide the window one sample at a time: add the newcomer, drop the oldest.
    # O(1) per step instead of re-adding `window` values.
    for i in range(window, len(samples)):
        s += samples[i] - samples[i - window]
        if s > best:
            best = s

    # Dividing by a positive constant doesn't change which window is largest,
    # so we compare sums and divide only once.
    return best / window
''',
    refs={
        "espresso": r'''// Sliding-window sum. The accumulator starts at 0.0: if it started at 0 and all
// samples happened to be whole numbers, sum / window would be an *integer* division.
fn peakAverage(samples, window) {
    var s = 0.0
    for var i in 0..window { s += samples[i] }
    var best = s
    for var i in window..len(samples) {
        s += samples[i] - samples[i - window]   // newcomer in, oldest out
        if s > best { best = s }
    }
    return best / window
}
''',
        "cpp": r'''double peakAverage(vector<double>& samples, long long window) {
    double s = accumulate(samples.begin(), samples.begin() + window, 0.0);
    double best = s;
    for (size_t i = window; i < samples.size(); i++) {
        s += samples[i] - samples[i - window];
        best = max(best, s);
    }
    return best / window;
}
''',
        "rust": r'''pub fn peak_average(samples: Vec<f64>, window: i64) -> f64 {
    let w = window as usize;
    let mut s: f64 = samples[..w].iter().sum();
    let mut best = s;
    for i in w..samples.len() {
        s += samples[i] - samples[i - w];
        best = best.max(s);
    }
    best / w as f64
}
''',
    },
    explanation=r"""
## Intuition

Consecutive windows overlap in all but two samples:

```text
 [ a  b  c  d ] e  f
   a [ b  c  d  e ] f      new sum = old sum − a + e
```

So keep a running sum and update it in O(1). Firmware does the same with a small circular
buffer of the last `window` readings: subtract the value about to be overwritten, add the
new reading, and the average is always one division (or, for a power-of-two window, one
shift) away.

## Approach

1. Sum the first `window` samples; that's the current best.
2. For each later index `i`: `s += samples[i] − samples[i − window]`; keep the max.
3. Return `best / window`.

Trace example 2 (`window = 4`):

| window | sum | avg |
|---|---|---|
| 20.5 21.0 35.5 21.5 | 98.5 | 24.625 |
| 21.0 35.5 21.5 22.0 | 100.0 | 25.0 |
| 35.5 21.5 22.0 22.5 | 101.5 | **25.375** |
| 21.5 22.0 22.5 23.0 | 89.0 | 22.25 |
| 22.0 22.5 23.0 22.5 | 90.0 | 22.5 |

The spike sits in three windows. The winner is the one that pairs it with the larger
neighbours, which is why you have to compare every window, not just the one centred on the spike.

## Complexity

O(n) time, O(1) extra space (O(window) for the circular buffer in a streaming version).

## Common mistakes

- **Integer division in ESPresso/C.** If the accumulator is an int, `sum / window`
  truncates. Start at `0.0` (or cast).
- **Off-by-one in the slide**: the element leaving is `samples[i − window]`, not
  `samples[i − window + 1]`.
- **Initialising `best = 0`.** All-negative input (example 5) then returns 0. Start from
  the first window.
- **Floating-point drift.** Long-running add/subtract SMAs accumulate rounding error.
  Here every value is a multiple of 0.5, which binary floats represent exactly, so there is
  none. On real hardware, keep the sum as an integer in sensor counts. That is exact
  forever.

## Going further

An **exponential** moving average, `avg += (x − avg) / 2ᵏ`, needs no buffer at all, just
one variable, and is the most common embedded filter. In fixed point it's `acc += x − (acc >> k)`,
with the average being `acc >> k`.
""",
    tests=_ma_tests,
))

# ---------------------------------------------------------------- 8. ring buffer
def _fifo_ops(rng, n, cap):
    ops = []
    for _ in range(n):
        ops.append(-1 if rng.random() < 0.4 else rng.randint(0, 255))
    return ops


_rb_tests = [
    [2, [10, 20, 30, -1, 40, -1, -1, -1]],
    [3, [-1, 5, -1, -1]],
    [1, [7, 8, -1, 9, -1]],
    [4, [1, 2, 3, 4, -1, -1, 5, 6, 7, -1, -1, -1, -1, -1]],
    [16, [0, 255, -1, -1]],
]
for _cap, _n in ((3, 16), (2, 15), (5, 18)):
    _rb_tests.append([_cap, _fifo_ops(_rng, _n, _cap)])
PROBLEMS.append(dict(
    id="uart-ring-buffer",
    title="UART Ring Buffer",
    difficulty=2,
    tags=["queue", "ring buffer", "simulation", "embedded"],
    fn="uart_fifo",
    params=[["capacity", "int"], ["ops", "int[]"]],
    returns="void",
    mutates="ops",
    statement=r"""
A UART receive interrupt drops each incoming byte into a **ring buffer** (circular FIFO),
and the main loop reads bytes out at its own pace. Memory is static: the buffer holds
at most `capacity` bytes, and when it is full, new bytes are **dropped** (the oldest
data is kept).

Simulate the buffer over the event list `ops` and **overwrite each entry in place**
with its result:

| event `ops[i]` | meaning | write back |
|---|---|---|
| `0 … 255` | a byte arrives | `1` if stored, `0` if dropped (buffer full) |
| `-1` | the main loop reads | the oldest byte (removing it), or `-1` if empty |

The buffer starts empty.
""",
    constraints=["`1 ≤ capacity ≤ 16`", "`0 ≤ len(ops) ≤ 30`", "`ops[i] = -1` or `0 ≤ ops[i] ≤ 255`"],
    example_notes=[
        "Capacity 2: `10` and `20` are stored, `30` is dropped. The read returns `10`, which frees a slot for `40`. Then the reads return `20`, `40`, and `-1` (empty).",
        "Reading from an empty buffer yields `-1`; the `5` is stored and read back once.",
    ],
    hints=[
        "Use a fixed array of `capacity` slots plus three integers: `head` (next read), `tail` (next write) and `count`.",
        "Advance an index with `i = i + 1; if i == capacity: i = 0`. That's modulo without dividing.",
        "`count` tells full (`== capacity`) from empty (`== 0`), which `head == tail` alone cannot. In ESPresso, allocate a 16-element literal, the maximum capacity.",
    ],
    solution=r'''def uart_fifo(capacity, ops):
    buf = [0] * capacity   # static storage, allocated once
    head = 0               # index of the oldest byte (next to read)
    tail = 0               # index where the next byte will be written
    count = 0              # bytes currently stored; disambiguates full vs empty

    for i, op in enumerate(ops):
        if op >= 0:                        # a byte arrived from the wire
            if count == capacity:
                ops[i] = 0                 # full: drop the new byte
            else:
                buf[tail] = op
                tail = (tail + 1) % capacity   # wrap around the end of the array
                count += 1
                ops[i] = 1
        else:                              # the main loop wants a byte
            if count == 0:
                ops[i] = -1                # nothing to read
            else:
                ops[i] = buf[head]
                head = (head + 1) % capacity
                count -= 1
''',
    refs={
        "espresso": r'''// ESPresso arrays can't be allocated with a runtime size, so do what firmware
// does: reserve the maximum (16 bytes) statically and use only `capacity` of it.
fn uartFifo(capacity, ops) {
    var buf = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    var head = 0
    var tail = 0
    var count = 0
    for var i in 0..len(ops) {
        if ops[i] >= 0 {
            if count == capacity {
                ops[i] = 0                      // overflow: byte lost
            } else {
                buf[tail] = ops[i]
                tail += 1
                if tail == capacity { tail = 0 } // wrap without % (ESPresso has none)
                count += 1
                ops[i] = 1
            }
        } else {
            if count == 0 {
                ops[i] = -1                     // underflow: nothing to read
            } else {
                ops[i] = buf[head]
                head += 1
                if head == capacity { head = 0 }
                count -= 1
            }
        }
    }
}
''',
        "cpp": r'''// Fixed-size std::array, like a static buffer in firmware.
void uartFifo(long long capacity, vector<long long>& ops) {
    array<long long, 16> buf{};
    long long head = 0, tail = 0, count = 0;
    for (auto& op : ops) {
        if (op >= 0) {
            if (count == capacity) { op = 0; continue; }
            buf[tail] = op;
            tail = (tail + 1) % capacity;
            count++;
            op = 1;
        } else if (count == 0) {
            op = -1;
        } else {
            op = buf[head];
            head = (head + 1) % capacity;
            count--;
        }
    }
}
''',
        "rust": r'''pub fn uart_fifo(capacity: i64, ops: &mut Vec<i64>) {
    let cap = capacity as usize;
    let mut buf = [0i64; 16];
    let (mut head, mut tail, mut count) = (0usize, 0usize, 0usize);
    for op in ops.iter_mut() {
        if *op >= 0 {
            if count == cap {
                *op = 0;
            } else {
                buf[tail] = *op;
                tail = (tail + 1) % cap;
                count += 1;
                *op = 1;
            }
        } else if count == 0 {
            *op = -1;
        } else {
            *op = buf[head];
            head = (head + 1) % cap;
            count -= 1;
        }
    }
}
''',
    },
    explanation=r"""
## Intuition

A queue in a fixed array would normally need shifting after every read. A **ring buffer**
avoids that by letting both ends chase each other around the array:

```text
capacity 4, after writes 1 2 3 4, reads → 1 2, writes 5 6:

 index:  0   1   2   3
 buf:  [ 5 | 6 | 3 | 4 ]
              ▲   ▲
           tail  head        count = 4 (full)
```

Reads come from `head`, writes go to `tail`, and both wrap from the last slot to 0.
This is the standard data structure between an interrupt and the main loop, because
each side writes only its own index.

## Approach

State: `buf[capacity]`, `head`, `tail`, `count`.

- **Write** (byte arrives): if `count == capacity` drop it (`0`); else store at `tail`,
  advance `tail`, `count++` (`1`).
- **Read** (`-1`): if `count == 0` → `-1`; else take `buf[head]`, advance `head`, `count--`.

Trace example 1 (capacity 2):

| op | buf | head | tail | count | written |
|---|---|---|---|---|---|
| 10 | [10, _] | 0 | 1 | 1 | 1 |
| 20 | [10, 20] | 0 | 0 | 2 | 1 |
| 30 | full | 0 | 0 | 2 | 0 |
| −1 | [_, 20] | 1 | 0 | 1 | 10 |
| 40 | [40, 20] | 1 | 1 | 2 | 1 |
| −1 | | 0 | 1 | 1 | 20 |
| −1 | | 1 | 1 | 0 | 40 |
| −1 | empty | | | 0 | −1 |

## Complexity

O(1) per operation, O(n) overall; O(capacity) memory, allocated once.

## Common mistakes

- **Full vs empty ambiguity.** With only `head` and `tail`, `head == tail` means both
  "empty" and "full". Fixes: a `count`, or sacrificing one slot (full when
  `tail + 1 == head`).
- **Forgetting to wrap** an index, then writing past the end of the array.
- **Overwrite-oldest vs drop-newest.** Both policies exist (audio streams often overwrite;
  serial protocols drop and flag an overrun). Read the spec.
- **Wrapping with `%` in ESPresso**: there is none; the compare-and-reset idiom is both
  legal and cheaper.

## Going further

With a power-of-two capacity you can let `head` and `tail` run freely and index with
`head & (N − 1)`; `tail − head` is then the count, even across integer wrap-around. That's
the trick behind Linux's `kfifo` and most lock-free single-producer/single-consumer queues.
""",
    tests=_rb_tests,
))

# ---------------------------------------------------------------- 9. BCD
def _bcd(v):
    return int(str(v), 16)


PROBLEMS.append(dict(
    id="bcd-counter-add",
    title="BCD Counter",
    difficulty=2,
    tags=["math", "digits", "embedded"],
    fn="bcd_add",
    params=[["a", "int"], ["b", "int"]],
    returns="int",
    statement=r"""
Real-time clock chips (DS1307, DS3231) and seven-segment drivers store numbers as
**packed BCD** (binary-coded decimal): each 4-bit nibble holds one decimal digit `0–9`.
The decimal number `1234` is stored as the hex value `0x1234`, which as a plain integer
is `4660`.

`a` and `b` are 4-digit packed-BCD values (`0x0000 … 0x9999`). Add the decimal numbers
they represent, keep only the last 4 decimal digits (the counter **rolls over** after
9999), and return the result packed as BCD.

Tests show the values as ordinary integers. For example `0x0010` appears as `16`.
""",
    constraints=["every nibble of `a` and `b` is a decimal digit 0–9", "`0 ≤ a, b ≤ 0x9999 = 39321`"],
    example_notes=[
        "`0x0001 + 0x0009` is `1 + 9 = 10`, packed as `0x0010 = 16`. A plain binary add would give `0x000A`, which isn't valid BCD.",
        "`0x9999` (9999) plus 1 rolls over to `0000`.",
    ],
    hints=[
        "Decode: the lowest nibble is `x mod 16`, and `x / 16` shifts the next one down. Weight them 1, 10, 100, 1000.",
        "Add the two decimal values, then reduce mod 10000.",
        "Encode the other way: take `n mod 10` and `n / 10` four times, weighting the digits 1, 16, 256, 4096. In ESPresso, `x mod m` is `x - (x / m) * m`.",
    ],
    solution=r'''def bcd_add(a, b):
    def decode(x):
        # Peel nibbles off the bottom: x % 16 is the low hex digit (a decimal
        # digit in valid BCD), x // 16 shifts the rest down by 4 bits.
        value, place = 0, 1
        for _ in range(4):
            value += (x % 16) * place
            x //= 16
            place *= 10
        return value

    def encode(n):
        # The reverse: peel decimal digits off with % 10 and place each one
        # in its own nibble (weights 1, 16, 256, 4096).
        packed, weight = 0, 1
        for _ in range(4):
            packed += (n % 10) * weight
            n //= 10
            weight *= 16
        return packed

    # A 4-digit counter rolls over after 9999.
    return encode((decode(a) + decode(b)) % 10000)
''',
    refs={
        "espresso": r'''// No bit operators and no %: shifts by 4 bits are "/ 16" and "* 16", and the
// low digit is x - (x / base) * base.
fn mod(x, m) {
    return x - (x / m) * m
}

fn bcdDecode(x) {
    var value = 0
    var place = 1
    for var i in 0..4 {
        value += mod(x, 16) * place   // low nibble = one decimal digit
        x = x / 16                    // shift right 4 bits
        place *= 10
    }
    return value
}

fn bcdEncode(n) {
    var packed = 0
    var weight = 1
    for var i in 0..4 {
        packed += mod(n, 10) * weight // low decimal digit into its nibble
        n = n / 10
        weight *= 16                  // next nibble
    }
    return packed
}

fn bcdAdd(a, b) {
    return bcdEncode(mod(bcdDecode(a) + bcdDecode(b), 10000))
}
''',
        "cpp": r'''// With real bit operators: nibble = (x >> 4*i) & 0xF.
long long bcdAdd(long long a, long long b) {
    auto dec = [](long long x) {
        long long v = 0, p = 1;
        for (int i = 0; i < 4; i++, p *= 10) v += ((x >> (4 * i)) & 0xF) * p;
        return v;
    };
    long long n = (dec(a) + dec(b)) % 10000, out = 0;
    for (int i = 0; i < 4; i++, n /= 10) out |= (n % 10) << (4 * i);
    return out;
}
''',
        "rust": r'''pub fn bcd_add(a: i64, b: i64) -> i64 {
    let dec = |x: i64| (0..4).map(|i| ((x >> (4 * i)) & 0xF) * 10i64.pow(i)).sum::<i64>();
    let mut n = (dec(a) + dec(b)) % 10000;
    let mut out = 0;
    for i in 0..4 {
        out |= (n % 10) << (4 * i);
        n /= 10;
    }
    out
}
''',
    },
    explanation=r"""
## Intuition

BCD trades storage for convenience: each decimal digit gets its own nibble, so a display
driver can send nibble *k* straight to digit *k* with no division. The cost is that
binary arithmetic doesn't respect the digit boundaries. `0x09 + 0x01 = 0x0A`, which
isn't a decimal digit. CPUs once had special instructions to fix this up (`DAA`, decimal
adjust after addition, on the 8080/x86). The portable route is **decode → add → encode**.

```text
 0x1234  =  0001 0010 0011 0100
              1    2    3    4      ← one decimal digit per nibble
```

## Approach

1. **Decode** each input: repeatedly take `x mod 16` (lowest nibble) and `x / 16` (shift
   right by 4), weighting the digits by 1, 10, 100, 1000.
2. Add, then take `mod 10000` (the 4-digit rollover).
3. **Encode**: repeatedly take `n mod 10` and `n / 10`, weighting by 1, 16, 256, 4096.

Trace `bcd_add(0x1234, 0x8765)` = `bcd_add(4660, 34661)`:

| step | value |
|---|---|
| decode(4660) | 1234 |
| decode(34661) | 8765 |
| sum mod 10000 | 9999 |
| encode(9999) | `0x9999 = 39321` |

## Complexity

O(digits) = O(1).

## Common mistakes

- **Mixing up the two radices**: decoding uses base 16 for extraction and base 10 for
  weights; encoding is the opposite.
- **Forgetting the rollover**: `0x9999 + 0x9999` must give `0x9998`, not a 5-digit value.
- **Hex vs decimal in the tests**: `16` *is* `0x0010`. Convert the expected outputs to hex
  in your head (or with `hex()` in Python) when debugging.
- **ESPresso:** no `%` (use the `mod` helper) and no `>>` (use `/ 16`, which is a shift
  for non-negative values).

## Going further

Implement the add digit by digit, as `DAA` does: add nibbles with a carry, and whenever a
nibble sum exceeds 9, add 6 to skip the six invalid codes `A–F`. It's also how an RTC's
seconds register ticks from `0x59` to `0x00` with a carry into the minutes.
""",
    tests=[
        [_bcd(1), _bcd(9)],
        [_bcd(9999), _bcd(1)],
        [_bcd(1234), _bcd(8765)],
        [_bcd(500), _bcd(500)],
        [0, 0],
        [_bcd(4999), _bcd(5001)],
        [_bcd(2718), _bcd(3141)],
        [_bcd(9999), _bcd(9999)],
        [_bcd(59), _bcd(1)],
        [_bcd(5), 0],
    ],
))

# ---------------------------------------------------------------- 10. LED overlap
_led_tests = [
    [[4, 6], [2, 3], 24],
    [[10], [3], 25],
    [[2, 3, 5], [1, 1, 1], 60],
    [[7, 7], [7, 1], 15],
    [[1], [1], 0],
    [[100, 60], [50, 30], 1000],
]
for _k in (3, 5):
    _ps = [_rng.randint(2, 40) for _ in range(_k)]
    _led_tests.append([_ps, [_rng.randint(1, p) for p in _ps], 1500])
PROBLEMS.append(dict(
    id="blinking-leds",
    title="Blinking LEDs",
    difficulty=2,
    tags=["simulation", "closures", "modulo", "embedded"],
    fn="led_overlap",
    params=[["periods", "int[]"], ["duties", "int[]"], ["ticks", "int"]],
    returns="int",
    statement=r"""
A status board has several LEDs, each blinking from its own software timer. LED `i`
repeats a cycle of `periods[i]` ticks: it is **on** for the first `duties[i]` ticks of
each cycle and off for the rest. Formally, at tick `t` LED `i` is on iff

```text
t mod periods[i] < duties[i]
```

All LEDs start their cycle at tick 0. Count the ticks `t` in `[0, ticks)` at which
**every** LED is on at the same time (that's when the board draws peak current).
""",
    constraints=["`1 ≤ len(periods) = len(duties) ≤ 8`", "`1 ≤ duties[i] ≤ periods[i] ≤ 100`", "`0 ≤ ticks ≤ 2000`"],
    example_notes=[
        "LED 0 is on at ticks `0,1, 4,5, 8,9, …`; LED 1 at `0,1,2, 6,7,8, …`. Both are on at `0, 1, 8`, and the pattern repeats every 12 ticks (`12, 13, 20`), so 6 ticks in 24.",
        "A single LED, on 3 of every 10 ticks: ticks 0–2, 10–12, 20–22, so 9.",
    ],
    hints=[
        "Simulate tick by tick: for each tick, check every LED.",
        "In ESPresso there is no `%`. Either use `t - (t / p) * p`, or give each LED its own phase counter that you advance and wrap.",
        "A closure is a neat home for that per-LED counter: `makeBlinker(period, duty)` returns a function that reports on/off and advances one tick. Be sure to advance **every** LED each tick, even after you already know the answer is \"no\".",
    ],
    solution=r'''def led_overlap(periods, duties, ticks):
    count = 0
    for t in range(ticks):
        # An LED is on during the first duties[i] ticks of each cycle of periods[i].
        if all(t % p < d for p, d in zip(periods, duties)):
            count += 1
    return count
''',
    refs={
        "espresso": r'''// Each LED is a closure that owns its phase counter, like a software timer
// object. No modulo needed: the phase wraps when it hits the period.
fn makeBlinker(period, duty) {
    var phase = 0
    fn step() {
        var on = phase < duty
        phase += 1
        if phase == period { phase = 0 }
        return on
    }
    return step
}

fn ledOverlap(periods, duties, ticks) {
    // Arrays can't grow, so reserve one slot per possible LED (max 8).
    var leds = [null, null, null, null, null, null, null, null]
    var n = len(periods)
    for var i in 0..n { leds[i] = makeBlinker(periods[i], duties[i]) }

    var count = 0
    for var t in 0..ticks {
        var allOn = true
        for var i in 0..n {
            var led = leds[i]
            if !led() { allOn = false }   // still step every LED: they all keep time
        }
        if allOn { count += 1 }
    }
    return count
}
''',
        "cpp": r'''long long ledOverlap(vector<long long>& periods, vector<long long>& duties, long long ticks) {
    long long count = 0;
    for (long long t = 0; t < ticks; t++) {
        bool all = true;
        for (size_t i = 0; i < periods.size() && all; i++) all = t % periods[i] < duties[i];
        count += all;
    }
    return count;
}
''',
        "rust": r'''pub fn led_overlap(periods: Vec<i64>, duties: Vec<i64>, ticks: i64) -> i64 {
    (0..ticks)
        .filter(|&t| periods.iter().zip(&duties).all(|(&p, &d)| t % p < d))
        .count() as i64
}
''',
    },
    explanation=r"""
## Intuition

Each LED is a tiny periodic state machine. The stateless way to ask "is it on at tick
`t`?" is `t mod period < duty`. The stateful way, the one firmware uses, is to keep
a **phase counter** per LED, increment it every tick and reset it at the period. The
second needs no division at all, and in ESPresso it fits **closures** naturally: each
`makeBlinker` call creates a fresh `phase` variable that only its `step` function can
see.

```text
period 4, duty 2:  t: 0 1 2 3 4 5 6 7 8
                  on: █ █ · · █ █ · · █
period 6, duty 3:     █ █ █ · · · █ █ █
both:                 █ █ · · · · · · █
```

## Approach

For each tick, AND together the LEDs' states, and count the ticks where the result is
true.

ESPresso version:

1. Build one closure per LED and store them in a pre-sized array (`[null × 8]`: arrays
   can't grow).
2. Each tick, call every closure exactly once, so all phases advance together, and track
   whether all returned `true`.

## Complexity

O(ticks · L) time for L LEDs, O(L) space. With up to 8 LEDs and 2000 ticks that's 16 000
checks.

## Common mistakes

- **Short-circuiting the closure calls.** With `if all and led()`, an LED that isn't asked
  doesn't advance its phase, so its timing drifts. The stateless `t mod p` version has no
  such trap, which is why the C++/Rust references can short-circuit safely.
- **Inclusive duty**: on means `phase < duty`, so a duty equal to the period is "always on".
- **Starting phases at 1** instead of 0.

## Going further

The pattern repeats every `lcm(periods)` ticks, so for huge `ticks` you could count one
period and multiply, then handle the remainder. With large coprime periods the LCM itself
blows up, which is exactly the overflow trap a 32-bit target would hit.
""",
    tests=_led_tests,
))

# ---------------------------------------------------------------- 11. FIR
def _fir_case(rng, n, taps, big=False):
    lim = 32767 if big else 2000
    return [[rng.randint(-lim, lim) for _ in range(n)], taps]


_fir_tests = [
    [[256, 512, 768, 1024], [128, 128]],
    [[100, 100, 100, 100, 100], [64, 64, 64, 64]],
    [[1, 2, 3], [256]],
    [[1, -1, 1, -1], [-128, 0, 0]],
    [[32767, 32767, 32767, 32767], [512, 512, 512]],
    [[-32768, -32768, 0], [512, 512]],
]
_fir_tests.append(_fir_case(_rng, 12, [32, 64, 96, 64]))
_fir_tests.append(_fir_case(_rng, 10, [400, -300, 200], big=True))
PROBLEMS.append(dict(
    id="fixed-point-fir",
    title="Fixed-Point FIR Filter",
    difficulty=3,
    tags=["fixed point", "in-place", "array", "embedded"],
    fn="fir_q8",
    params=[["samples", "int[]"], ["taps", "int[]"]],
    returns="void",
    mutates="samples",
    statement=r"""
A **FIR filter** computes each output as a weighted sum of the current and previous
inputs. Here the weights (`taps`) are in **Q8 fixed point**: the integer `256` means
`1.0`, `128` means `0.5`, `-64` means `-0.25`.

For each index `n`:

```text
acc[n] = Σ taps[k] · samples[n − k]      for k = 0 … len(taps) − 1
         (samples before index 0 count as 0)
```

Convert `acc[n]` from Q8 to an integer **rounding half away from zero**
(`(acc + 128) / 256` for `acc ≥ 0`, and `−((−acc + 128) / 256)` for `acc < 0`, with
truncating division), then **saturate** to the int16 range `[-32768, 32767]`.

Overwrite `samples` **in place** with the outputs. There's no room for a second
buffer, so make sure each output uses the **original** input values.
""",
    constraints=["`1 ≤ len(samples) ≤ 16`", "`1 ≤ len(taps) ≤ 4`", "`|samples[i]| ≤ 32768`", "`|taps[k]| ≤ 512`"],
    example_notes=[
        "Taps `[0.5, 0.5]` average each sample with the previous one. Index 0 averages with an implicit 0: `256 · 0.5 = 128`. Then `(512+256)/2 = 384`, `640`, `896`.",
        "A 4-tap averager warms up: `25, 50, 75, 100, 100`.",
    ],
    hints=[
        "Out-of-place first: compute each output into a new array and check the rounding and saturation.",
        "Output `n` reads inputs `n, n−1, …`, never later ones. Which order of `n` lets you overwrite safely?",
        "Iterate `n` from the last index down to 0: by the time you overwrite `samples[n]`, no remaining output needs it.",
        "Round on magnitudes: `y = (|acc| + 128) / 256`, then restore the sign; clamp last.",
    ],
    solution=r'''def fir_q8(samples, taps):
    # Output n depends only on inputs at indices <= n. Walking n from the END
    # means we overwrite samples[n] only after every output that reads it
    # (n, n+1, ...) has already been computed.
    for n in range(len(samples) - 1, -1, -1):
        acc = 0
        for k, t in enumerate(taps):
            if n - k >= 0:                 # inputs before the start are zero
                acc += t * samples[n - k]  # Q8 tap * integer sample = Q8 product

        # Q8 -> integer, rounding half away from zero. Rounding the magnitude
        # and reapplying the sign keeps the behaviour symmetric for negatives.
        mag = (abs(acc) + 128) // 256
        y = mag if acc >= 0 else -mag

        # Saturate to int16 instead of letting the value wrap around.
        samples[n] = max(-32768, min(32767, y))
''',
    refs={
        "espresso": r'''// In-place FIR: iterate from the last sample backwards so that every input we
// still need is untouched when we read it.
fn firQ8(samples, taps) {
    var n = len(samples) - 1
    while n >= 0 {
        var acc = 0
        for var k in 0..len(taps) {
            if n - k >= 0 { acc += taps[k] * samples[n - k] }   // |acc| < 2^31 by constraints
        }
        var y = 0
        if acc >= 0 {
            y = (acc + 128) / 256          // round half up on the magnitude...
        } else {
            y = -((-acc + 128) / 256)      // ...and mirror it for negatives
        }
        if y > 32767 { y = 32767 }         // saturate to int16
        if y < -32768 { y = -32768 }
        samples[n] = y
        n -= 1
    }
}
''',
        "cpp": r'''void firQ8(vector<long long>& samples, vector<long long>& taps) {
    for (int n = (int)samples.size() - 1; n >= 0; n--) {
        long long acc = 0;
        for (int k = 0; k < (int)taps.size() && n - k >= 0; k++) acc += taps[k] * samples[n - k];
        long long mag = (llabs(acc) + 128) / 256;
        samples[n] = clamp(acc >= 0 ? mag : -mag, -32768LL, 32767LL);
    }
}
''',
        "rust": r'''pub fn fir_q8(samples: &mut Vec<i64>, taps: Vec<i64>) {
    for n in (0..samples.len()).rev() {
        let acc: i64 = taps.iter().enumerate()
            .filter(|(k, _)| *k <= n)
            .map(|(k, t)| t * samples[n - k])
            .sum();
        let mag = (acc.abs() + 128) / 256;
        samples[n] = (if acc >= 0 { mag } else { -mag }).clamp(-32768, 32767);
    }
}
''',
    },
    explanation=r"""
## Intuition

Three embedded skills meet here.

1. **Fixed-point multiply.** A Q8 tap times an integer sample gives a Q8 product. Sum
   them all at full precision (the *accumulator*, like a DSP's wide MAC register) and
   convert **once** at the end. Rounding each product separately would add error per tap.
2. **Rounding and saturation.** `+128` before `/256` rounds to nearest; doing it on the
   magnitude makes `−0.5` round to `−1` just as `0.5` rounds to `1`. The int16 clamp
   replaces wrap-around, which would turn a loud positive peak into a loud negative click.
3. **In-place processing.** Output `n` reads `samples[n−k]` for `k ≥ 0`: only the current
   and **earlier** indices. Going **backwards**, every index you still need is untouched.

```text
forward (wrong):   y[1] needs x[0], but x[0] was already replaced by y[0]
backward (right):  y[3] uses x[3],x[2],x[1] → write y[3]; y[2] uses x[2],x[1],x[0] ...
```

## Approach

Trace example 1, taps `[128, 128]` (0.5, 0.5), going backwards:

| n | acc | rounded | output |
|---|---|---|---|
| 3 | 128·1024 + 128·768 = 229376 | (229376+128)/256 = 896 | 896 |
| 2 | 128·768 + 128·512 = 163840 | 640 | 640 |
| 1 | 128·512 + 128·256 = 98304 | 384 | 384 |
| 0 | 128·256 + 0 = 32768 | 128 | 128 |

## Complexity

O(n · taps) time, O(1) extra space, which is the point of doing it in place.

## Common mistakes

- **Iterating forward in place**: later outputs read already-filtered values. That
  computes an IIR-ish smear instead of the FIR.
- **Rounding negatives with `(acc + 128) / 256`**: with truncating division, `acc = −200`
  gives `−72/256 = 0`, but the correct result rounds `−0.78` to `−1`.
- **Python `//` with negatives** floors; use the magnitude trick so all languages agree.
- **Overflow.** The constraints keep `|acc| ≤ 4 · 512 · 32768 = 2²⁶`, safe in 32 bits. Real
  audio DSPs use Q15 taps and 40-bit accumulators for this reason.
- **Clamping before rounding**: clamp last.

## Going further

Real systems run FIRs on a stream: keep the last `len(taps) − 1` inputs in a small ring
buffer (problem 8) and produce one output per new sample. Then try a 2-pole IIR biquad.
Feedback makes rounding errors recirculate, which is where fixed-point design really bites.
""",
    tests=_fir_tests,
))

# ---------------------------------------------------------------- 12. PID
def _plant(rng, n, sp):
    m, out = rng.randint(0, 200), []
    for _ in range(n):
        out.append(m)
        m = max(-1000, min(1000, m + rng.randint(-40, 60) + (sp - m) // 4))
    return out


_pid_tests = [
    [500, [0, 100, 250, 400, 480, 510, 505], 256, 0, 0],
    [100, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0, 64, 0],
    [0, [0, 50, 20, -30, 0], 0, 0, 512],
    [300, [0, 50, 120, 200, 260, 290, 310, 305], 300, 40, 600],
    [-200, [0, -50, -120, -180, -210], 256, 32, 128],
]
for _sp, _g in ((400, (220, 50, 300)), (-300, (512, 128, 1024)), (700, (128, 256, 64))):
    _pid_tests.append([_sp, _plant(_rng, 10, _sp), *_g])
PROBLEMS.append(dict(
    id="pid-motor-controller",
    title="PID Motor Controller",
    difficulty=3,
    tags=["simulation", "fixed point", "control", "embedded"],
    fn="pid_controller",
    params=[["setpoint", "int"], ["measurements", "int[]"], ["kp", "int"], ["ki", "int"], ["kd", "int"]],
    returns="void",
    mutates="measurements",
    statement=r"""
A DC motor's speed is controlled by an integer **PID** loop running once per tick. The
gains `kp`, `ki`, `kd` are **Q8 fixed point** (`256` = 1.0). The output drives an
H-bridge with a signed 8-bit PWM command (`−255…255`: the sign is the direction).

Process the ticks in order. Before the first tick, `integral = 0`. For each measurement `m`:

1. `error = setpoint − m`
2. `integral = integral + error`, then **clamp** it to `[-1000, 1000]` (anti-windup)
3. `derivative = error − previous_error`, except on the **first** tick, where it is `0`
4. `u = kp·error + ki·integral + kd·derivative`
5. `out = u / 256` with **truncation toward zero**, then clamp to `[-255, 255]`
6. remember `previous_error = error`

Overwrite `measurements[i]` with the output for tick `i`.
""",
    constraints=["`1 ≤ len(measurements) ≤ 12`", "`|setpoint|, |measurements[i]| ≤ 1000`", "`0 ≤ kp, ki, kd ≤ 1024`"],
    example_notes=[
        "Pure P control with gain 1.0: the output is just the error, clamped to ±255. So `500, 400, 250, 100, 20, -10, -5`, with the first two clamped to `255`.",
        "Pure I control (gain 0.25): the integral grows by 100 each tick until the anti-windup clamp holds it at 1000, so the output climbs `25, 50, …, 200, 250, 250`.",
    ],
    hints=[
        "This is a direct simulation. Get the order of steps right, especially clamping the integral *before* using it.",
        "Use a flag (or a `None` previous error) so the first tick's derivative is 0.",
        "Truncation toward zero matters for negative `u`: in Python, `-(abs(u) // 256)` for negative `u`. ESPresso, C, C++ and Rust truncate natively.",
    ],
    solution=r'''def pid_controller(setpoint, measurements, kp, ki, kd):
    integral = 0
    prev_error = None          # no previous error before the first tick

    for i, m in enumerate(measurements):
        error = setpoint - m

        # Integrate, then clamp: anti-windup stops the integral from growing
        # without bound while the output is saturated.
        integral = max(-1000, min(1000, integral + error))

        # Derivative of the error; defined as 0 on the first tick so the
        # controller doesn't "kick" on start-up.
        derivative = 0 if prev_error is None else error - prev_error
        prev_error = error

        # Q8 gains: the sum is in Q8, so divide by 256 to get the PWM command.
        u = kp * error + ki * integral + kd * derivative
        out = abs(u) // 256            # truncate toward zero, like C's "/" ...
        if u < 0:
            out = -out                 # ... by rounding the magnitude down

        # The H-bridge accepts -255..255.
        measurements[i] = max(-255, min(255, out))
''',
    refs={
        "espresso": r'''// Integer PID. ESPresso's "/" truncates toward zero, exactly as specified.
// The `first` flag keeps the derivative at 0 on the first tick.
fn clamp(v, lo, hi) {
    if v < lo { return lo }
    if v > hi { return hi }
    return v
}

fn pidController(setpoint, measurements, kp, ki, kd) {
    var integral = 0
    var prevError = 0
    var first = true
    for var i in 0..len(measurements) {
        var error = setpoint - measurements[i]
        integral = clamp(integral + error, -1000, 1000)   // anti-windup
        var derivative = 0
        if !first { derivative = error - prevError }
        first = false
        prevError = error
        var u = kp * error + ki * integral + kd * derivative   // Q8, < 2^31 by constraints
        measurements[i] = clamp(u / 256, -255, 255)            // Q8 -> PWM command
    }
}
''',
        "cpp": r'''void pidController(long long setpoint, vector<long long>& measurements, long long kp, long long ki, long long kd) {
    long long integral = 0, prev = 0;
    for (size_t i = 0; i < measurements.size(); i++) {
        long long e = setpoint - measurements[i];
        integral = clamp(integral + e, -1000LL, 1000LL);
        long long d = i == 0 ? 0 : e - prev;
        prev = e;
        long long u = kp * e + ki * integral + kd * d;
        measurements[i] = clamp(u / 256, -255LL, 255LL);   // C++ "/" truncates toward zero
    }
}
''',
        "rust": r'''pub fn pid_controller(setpoint: i64, measurements: &mut Vec<i64>, kp: i64, ki: i64, kd: i64) {
    let mut integral = 0i64;
    let mut prev: Option<i64> = None;
    for m in measurements.iter_mut() {
        let e = setpoint - *m;
        integral = (integral + e).clamp(-1000, 1000);
        let d = prev.map_or(0, |p| e - p);
        prev = Some(e);
        let u = kp * e + ki * integral + kd * d;
        *m = (u / 256).clamp(-255, 255);   // Rust "/" truncates toward zero
    }
}
''',
    },
    explanation=r"""
## Intuition

A PID controller adds three opinions about the error:

- **P**roportional: push in proportion to how far off we are *now*.
- **I**ntegral: push harder the longer we've *been* off (removes steady-state error).
- **D**erivative: push back against how fast the error is *changing* (damping).

On a microcontroller each term is an integer multiply by a Q8 gain, and the sum is
scaled back with one divide. Two safety rails make it production-grade: **anti-windup**
(clamp the integral) and **output saturation** (the PWM can't exceed ±255).

## Approach

Follow the six steps exactly; the order is the spec. Trace the fourth test (setpoint 300,
kp = 300, ki = 40, kd = 600), first three ticks:

| tick | m | error | integral | deriv | u | out |
|---|---|---|---|---|---|---|
| 0 | 0 | 300 | 300 | 0 | 90000 + 12000 + 0 = 102000 | 398 → **255** |
| 1 | 50 | 250 | 550 | −50 | 75000 + 22000 − 30000 = 67000 | **261** → 255 |
| 2 | 120 | 180 | 730 | −70 | 54000 + 29200 − 42000 = 41200 | **160** |

The derivative term brakes as the motor approaches the setpoint, so the output drops before
the error reaches zero. That's the damping.

## Complexity

O(n) time, O(1) state: two integers and a flag. That's why PID is everywhere.

## Common mistakes

- **Using the unclamped integral** in `u`: clamp first, then multiply.
- **Derivative kick**: computing `error − 0` on the first tick produces a huge spike. The
  spec avoids it; real controllers often differentiate the *measurement* instead.
- **Rounding negative outputs**: `u = −300` must give `−1` (truncation), not `−2`
  (Python floor). Divide the magnitude, then reapply the sign.
- **Overflow on 32-bit targets**: `kd · derivative` can reach `1024 · 4000 ≈ 4·10⁶`, fine,
  but gains in Q16 or larger errors would need 64-bit accumulators.
- **Clamping the output before dividing** (that would clamp `u`, a Q8 value).

## Going further

- Anti-windup by **conditional integration**: stop integrating while the output is
  saturated, instead of a fixed integral clamp.
- Run the controller against a simulated plant: `speed += (out − speed / 4) / 8` per tick,
  then tune kp, ki and kd until the step response settles without overshoot.
""",
    tests=_pid_tests,
))

for _p in PROBLEMS:
    _esp_budget(_p)
