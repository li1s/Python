import asyncio

async def is_perfect_number(number):
    sum_of_divisors = 0
    divisors = []
    for i in range(1, number):
        if number % i == 0:
            sum_of_divisors += i
            divisors.append(i)
            await asyncio.sleep(0)  # Simulate some asynchronous operation
    return sum_of_divisors == number, divisors

async def find_perfect_numbers(start, end):
    perfect_numbers = []
    for num in range(start, end + 1):
        is_perfect, divisors = await is_perfect_number(num)
        if is_perfect:
            perfect_numbers.append((num, divisors))
    return perfect_numbers

async def main():
    start = int(input("Введите начало участка для поиска совершенных чисел: "))
    end = int(input("Введите конец участка для поиска совершенных чисел: "))
    perfect_numbers = await find_perfect_numbers(start, end)
    print("Совершенные числа в диапазоне от", start, "до", end, ":", perfect_numbers)

asyncio.run(main())

