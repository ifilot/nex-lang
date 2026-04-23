# Prime Number Examples

This folder contains a small set of examples built around prime numbers. The
goal is to show that NEX can express useful search-style algorithms even
without arrays or other collection types.

Run any example with:

```bash
python3 -m nex.cli examples/primes/<file>.nex
```

## Scripts

- `expensive_prime_scan.nex`: counts primes with a deliberately naive algorithm so you can feel how an expensive search behaves.
- `is_prime.nex`: defines a reusable `is_prime(...)` helper and checks a few sample values.
- `primes_in_range.nex`: prints every prime number in a closed interval.
- `first_n_primes.nex`: generates the first `N` prime numbers by testing candidates one by one.
- `next_prime.nex`: searches upward until it finds the next prime after a given starting value.
- `prime_factorization.nex`: prints the prime factors of a number by repeatedly dividing out each divisor.
