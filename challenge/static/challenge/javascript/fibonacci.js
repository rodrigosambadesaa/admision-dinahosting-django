class BigInteger {
    constructor(sign, digits) {
        this.sign = digits === "0" ? 0 : sign;
        this.digits = digits;
    }

    static zero() {
        return new BigInteger(0, "0");
    }

    static one() {
        return new BigInteger(1, "1");
    }

    static fromNumber(value) {
        if (!Number.isSafeInteger(value)) {
            throw new Error("Solo se aceptan enteros seguros.");
        }

        return BigInteger.fromString(String(value));
    }

    static fromString(value) {
        if (typeof value !== "string" || !/^[+-]?\d+$/.test(value)) {
            throw new Error("Valor BigInteger no válido.");
        }

        if (value.replace(/^[+-]/, "").length > 256) {
            throw new Error("El entero sintético supera los 256 dígitos permitidos.");
        }

        const normalized = value.replace(/^[+]/, "");
        const sign = normalized.startsWith("-") ? -1 : 1;
        const digits = normalized.replace(/^[+-]/, "").replace(/^0+(?=\d)/, "");

        return new BigInteger(digits === "0" ? 0 : sign, digits);
    }

    compare(other) {
        if (this.sign !== other.sign) {
            return this.sign < other.sign ? -1 : 1;
        }

        if (this.sign === 0) {
            return 0;
        }

        const magnitudeComparison = BigInteger.compareMagnitudes(this.digits, other.digits);

        return this.sign > 0 ? magnitudeComparison : -magnitudeComparison;
    }

    add(other) {
        if (this.sign === 0) {
            return other;
        }

        if (other.sign === 0) {
            return this;
        }

        if (this.sign === other.sign) {
            return new BigInteger(
                this.sign,
                BigInteger.addMagnitudes(this.digits, other.digits)
            );
        }

        const comparison = BigInteger.compareMagnitudes(this.digits, other.digits);

        if (comparison === 0) {
            return BigInteger.zero();
        }

        if (comparison > 0) {
            return new BigInteger(
                this.sign,
                BigInteger.subtractMagnitudes(this.digits, other.digits)
            );
        }

        return new BigInteger(
            other.sign,
            BigInteger.subtractMagnitudes(other.digits, this.digits)
        );
    }

    isNegative() {
        return this.sign < 0;
    }

    toString() {
        if (this.sign === 0) {
            return "0";
        }

        return this.sign < 0 ? `-${this.digits}` : this.digits;
    }

    static compareMagnitudes(left, right) {
        if (left.length !== right.length) {
            return left.length < right.length ? -1 : 1;
        }

        if (left === right) {
            return 0;
        }

        return left < right ? -1 : 1;
    }

    static addMagnitudes(left, right) {
        let carry = 0;
        let result = "";
        let leftIndex = left.length - 1;
        let rightIndex = right.length - 1;

        while (leftIndex >= 0 || rightIndex >= 0 || carry > 0) {
            const leftDigit = leftIndex >= 0 ? Number(left[leftIndex]) : 0;
            const rightDigit = rightIndex >= 0 ? Number(right[rightIndex]) : 0;
            const sum = leftDigit + rightDigit + carry;

            result = String(sum % 10) + result;
            carry = Math.floor(sum / 10);
            leftIndex -= 1;
            rightIndex -= 1;
        }

        return result;
    }

    static subtractMagnitudes(left, right) {
        let borrow = 0;
        let result = "";
        let leftIndex = left.length - 1;
        let rightIndex = right.length - 1;

        while (leftIndex >= 0) {
            let leftDigit = Number(left[leftIndex]) - borrow;
            const rightDigit = rightIndex >= 0 ? Number(right[rightIndex]) : 0;

            if (leftDigit < rightDigit) {
                leftDigit += 10;
                borrow = 1;
            } else {
                borrow = 0;
            }

            result = String(leftDigit - rightDigit) + result;
            leftIndex -= 1;
            rightIndex -= 1;
        }

        return result.replace(/^0+(?=\d)/, "");
    }
}

class FibonacciSequenceGenerator {
    generateUpTo(limit) {
        if (limit.isNegative()) {
            return [];
        }

        const zero = BigInteger.zero();
        const one = BigInteger.one();
        const sequence = [zero];

        if (limit.compare(zero) === 0) {
            return sequence;
        }

        sequence.push(one);

        let previous = zero;
        let current = one;

        while (true) {
            const next = previous.add(current);

            if (next.compare(limit) > 0) {
                break;
            }

            sequence.push(next);
            previous = current;
            current = next;
        }

        return sequence;
    }
}

class DateRange {
    constructor(startTimestamp, endTimestamp, startLabel, endLabel, timezone = "UTC") {
        if (startTimestamp.compare(endTimestamp) > 0) {
            [startTimestamp, endTimestamp] = [endTimestamp, startTimestamp];
            [startLabel, endLabel] = [endLabel, startLabel];
        }

        this.startTimestamp = startTimestamp;
        this.endTimestamp = endTimestamp;
        this.startLabel = startLabel;
        this.endLabel = endLabel;
        this.timezone = timezone;
    }
}

class BaseRangeProvider {
    constructor(label) {
        this.label = label;
    }
}

class CurrentMonthRangeProvider extends BaseRangeProvider {
    constructor() {
        super("Mes actual");
    }

    getRange() {
        const now = new Date();
        const start = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1, 0, 0, 0));
        const end = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 0, 23, 59, 59));
        const startLabel = formatUtcDateFromDate(start);
        const endLabel = formatUtcDateFromDate(end);

        return new DateRange(
            BigInteger.fromNumber(Math.floor(start.getTime() / 1000)),
            BigInteger.fromNumber(Math.floor(end.getTime() / 1000)),
            startLabel,
            endLabel
        );
    }
}

class CurrentYearRangeProvider extends BaseRangeProvider {
    constructor() {
        super("Año actual");
    }

    getRange() {
        const now = new Date();
        const start = new Date(Date.UTC(now.getUTCFullYear(), 0, 1, 0, 0, 0));
        const end = new Date(Date.UTC(now.getUTCFullYear(), 11, 31, 23, 59, 59));
        const startLabel = formatUtcDateFromDate(start);
        const endLabel = formatUtcDateFromDate(end);

        return new DateRange(
            BigInteger.fromNumber(Math.floor(start.getTime() / 1000)),
            BigInteger.fromNumber(Math.floor(end.getTime() / 1000)),
            startLabel,
            endLabel
        );
    }
}

class CustomRangeProvider extends BaseRangeProvider {
    constructor(startValue, endValue) {
        super("Rango personalizado");
        this.startValue = startValue;
        this.endValue = endValue;
    }

    getRange() {
        const startBoundary = parseRangeBoundary(this.startValue);
        const endBoundary = parseRangeBoundary(this.endValue);

        return new DateRange(
            startBoundary.timestamp,
            endBoundary.timestamp,
            startBoundary.label,
            endBoundary.label,
            startBoundary.timezone === endBoundary.timezone
                ? startBoundary.timezone
                : `${startBoundary.timezone} -> ${endBoundary.timezone}`
        );
    }
}

class FibonacciRangeResolver {
    constructor(generator) {
        this.generator = generator;
    }

    resolve(range) {
        return this.generator
            .generateUpTo(range.endTimestamp)
            .filter((value) => value.compare(range.startTimestamp) >= 0 && value.compare(range.endTimestamp) <= 0);
    }
}

function parseUtcDateTime(value) {
    const match = value.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/);

    if (!match) {
        throw new Error('Usa el formato "Y-m-d H:i:s".');
    }

    const parts = match.slice(1).map(Number);
    const [year, month, day, hour, minute, second] = parts;
    const date = new Date(0);
    // Date.UTC(0..99, ...) convierte los años 0000-0099 en 1900-1999.
    date.setUTCFullYear(year, month - 1, day);
    date.setUTCHours(hour, minute, second, 0);

    if (
        date.getUTCFullYear() !== year ||
        date.getUTCMonth() !== month - 1 ||
        date.getUTCDate() !== day ||
        date.getUTCHours() !== hour ||
        date.getUTCMinutes() !== minute ||
        date.getUTCSeconds() !== second
    ) {
        throw new Error("La fecha indicada no es válida.");
    }

    return BigInteger.fromNumber(Math.floor(date.getTime() / 1000));
}

function formatUtcDateFromDate(date) {
    const pad = (value) => String(value).padStart(2, "0");

    return `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())} ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}:${pad(date.getUTCSeconds())} UTC`;
}

function parseRangeBoundary(value) {
    if (value.startsWith("ts:")) {
        const raw = value.slice(3);

        if (!/^[+-]?\d+$/.test(raw)) {
            throw new Error('Usa el formato "ts:<bigint>" para timestamps sintéticos extremos.');
        }

        return {
            label: `ts:${raw}`,
            timestamp: BigInteger.fromString(raw),
            timezone: "synthetic-bigint"
        };
    }

    return {
        label: `${value} UTC`,
        timestamp: parseUtcDateTime(value),
        timezone: "UTC"
    };
}

function sanitizeDateInput(value) {
    if (typeof value !== "string") {
        throw new Error("La entrada recibida no es válida.");
    }

    const sanitized = value.trim();

    if (sanitized.length > 260 || (sanitized.startsWith("ts:")
        && sanitized.slice(3).replace(/^[+-]/, "").length > 256)) {
        throw new Error("La entrada supera el límite de 256 dígitos sintéticos.");
    }

    if (sanitized === "") {
        throw new Error("La entrada recibida no es válida.");
    }

    if (!/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|ts:[+-]?\d+)$/.test(sanitized)) {
        throw new Error('Usa "Y-m-d H:i:s" o "ts:<bigint>".');
    }

    return sanitized;
}

function createInfoParagraph(label, value) {
    const paragraph = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `${label}:`;
    paragraph.appendChild(strong);
    paragraph.append(` ${value}`);
    return paragraph;
}

function renderResults(container, sections) {
    container.replaceChildren();

    for (const section of sections) {
        const card = document.createElement("article");
        card.className = "result-card";

        const title = document.createElement("h2");
        title.textContent = section.label;
        card.appendChild(title);

        card.appendChild(createInfoParagraph("Inicio", section.range.startLabel));
        card.appendChild(createInfoParagraph("Fin", section.range.endLabel));
        card.appendChild(createInfoParagraph("Timezone / modo", section.range.timezone));

        if (section.values.length > 0) {
            const list = document.createElement("ul");
            list.className = "result-list";

            for (const value of section.values) {
                const item = document.createElement("li");
                item.textContent = value.toString();
                list.appendChild(item);
            }

            card.appendChild(list);
        } else {
            const emptyState = document.createElement("p");
            emptyState.className = "empty-state";
            emptyState.textContent = "No hay timestamps Fibonacci dentro de este rango.";
            card.appendChild(emptyState);
        }

        container.appendChild(card);
    }
}

if (typeof document !== "undefined") {
const form = document.getElementById("fibonacci-form");
const errorBox = document.getElementById("error-message");
const results = document.getElementById("results");

form.addEventListener("submit", (event) => {
    event.preventDefault();
    errorBox.textContent = "";

    try {
        const formData = new FormData(form);
        const providers = [
            new CurrentMonthRangeProvider(),
            new CurrentYearRangeProvider(),
            new CustomRangeProvider(
                sanitizeDateInput(formData.get("start_date")),
                sanitizeDateInput(formData.get("end_date"))
            )
        ];

        const resolver = new FibonacciRangeResolver(new FibonacciSequenceGenerator());
        const sections = providers.map((provider) => {
            const range = provider.getRange();

            return {
                label: provider.label,
                range,
                values: resolver.resolve(range)
            };
        });

        renderResults(results, sections);
    } catch (error) {
        results.replaceChildren();
        errorBox.textContent = error instanceof Error ? error.message : "Se ha producido un error no esperado.";
    }
});

}

// Exposición exclusiva para pruebas Node.js; en navegador se conserva el script clásico.
if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        BigInteger, FibonacciSequenceGenerator, DateRange,
        CurrentMonthRangeProvider, CurrentYearRangeProvider, CustomRangeProvider,
        FibonacciRangeResolver, parseUtcDateTime, sanitizeDateInput, parseRangeBoundary
    };
}
