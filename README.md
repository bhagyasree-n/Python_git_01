# Hex Block Reader

A small utility script that reads a `.hex` firmware image (`BlinkyApp.hex`) 6 bytes at a time, one block per script run, and remembers where it left off between runs.

## What it does

Each time you run the script, it:

1. Loads `BlinkyApp.hex` into memory using the `intelhex` library.
2. Figures out which 6-byte block to read next:
   - First run (or after `--reset`): starts at the file's lowest populated address (`min_addr`).
   - Every subsequent run: resumes from wherever the previous run left off, using a small state file (`read_state.json`).
3. If the next block would run past the end of the file's data (`max_addr`), it wraps around and starts again from `min_addr`.
4. Reads the 6 bytes at the current address and prints them as hex.
5. Saves the *next* address to `read_state.json` so the following run continues correctly.

This makes it useful for things like "step through the firmware image one block at a time on each button press / test cycle / cron tick."

## Requirements

- Python 3
- [`intelhex`](https://pypi.org/project/intelhex/) package

```bash
pip install intelhex
```

## Usage

Place `BlinkyApp.hex` in the same directory as the script (or update the `HEX_FILE` constant), then run:

```bash
python read_hex_block.py
```

Each run prints one block and advances the pointer:

```
Address = 0x08000000  |  Data = 00 20 00 20 D1 07
```

Run it again and it will print the *next* 6 bytes, and so on.

### Starting over

To clear the saved progress and start again from the beginning of the file:

```bash
python read_hex_block.py --reset
```

## How the code is organized

| Step | What happens | Where |
|---|---|---|
| Parse arguments | Reads the `--reset` flag | `parse_args()` |
| Load hex file | Loads `BlinkyApp.hex`, gets `min_addr` / `max_addr` | `main()`, via `IntelHex` |
| Handle reset | Deletes `read_state.json` if `--reset` was passed | `main()` |
| Determine start address | Reads `next_addr` from `read_state.json`, or falls back to `min_addr` | `main()` |
| Wraparound check | If the next block would exceed `max_addr`, resets to `min_addr` | `main()` |
| Read block | Reads 6 bytes starting at the current address and prints them | `main()` |
| Save state | Writes the next address to `read_state.json` for the following run | `main()` |

## Files

- `BlinkyApp.hex` — the Intel HEX firmware image being read (input, not modified).
- `read_state.json` — auto-created/updated by the script to track the next address to read. Safe to delete manually (equivalent to `--reset`).

## Notes / things to keep in mind

- `bytes_per_block` is currently hardcoded to `6`. Changing it mid-sequence (without resetting) can produce misaligned reads, since the saved `next_addr` was computed using the old block size.
- The wraparound check only look ahead by `bytes_per_block` bytes, so it assumes the hex file's address range is contiguous. If the actual populated hex data has internal gaps, `ih[addr + j]` will still return a value (`intelhex` returns `0xFF` — or `0x00`, per its padding config — for unset addresses within range) rather than raising an error.
- The state file uses whatever directory the script is run from, so running it from different working directories will read/write different `read_state.json` files.
