import logging
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

logger = logging.getLogger(__name__)


class QuantumCircuitService:
    """
    Service for creating, executing, and processing quantum circuits.
    """

    def __init__(self, shots=1024):
        """
        Initialize the quantum circuit service.

        Args:
            shots: Number of shots for quantum circuit execution
        """
        self.shots = shots
        self.simulator = AerSimulator()
        logger.info(f"Initialized QuantumCircuitService with {shots} shots")

    def execute_qasm(self, qasm_string):
        """
        Execute a quantum circuit from QASM string.

        Args:
            qasm_string: String containing QASM representation of a quantum circuit

        Returns:
            Dict containing the measurement results or error
        """
        try:
            processed_qasm = self._preprocess_qasm(qasm_string)
            logger.info(f"Processed QASM string:\n{processed_qasm}")

            circuit = QuantumCircuit.from_qasm_str(processed_qasm)
            logger.info(f"Successfully parsed QASM string into circuit with {circuit.num_qubits} qubits")

            # Execute the circuit
            result = self.simulator.run(circuit, shots=self.shots).result()
            counts = result.get_counts(circuit)

            logger.info(f"Circuit execution complete with {len(counts)} unique outcomes")
            formatted_counts = self.format_counts(counts)
            return {"error": False, "counts": formatted_counts}

        except Exception as e:
            logger.error(f"QASM parsing failed. Error: {str(e)}")
            return {"error": True, "message": str(e)}

    def _preprocess_qasm(self, qasm_string):
        """
        Preprocess QASM string to ensure compatibility.

        Args:
            qasm_string: Input QASM string

        Returns:
            Processed QASM string
        """
        # Handle QASM 3.0 to 2.0 conversion
        if "OPENQASM 3.0" in qasm_string:
            logger.info("Converting QASM 3.0 to QASM 2.0 format")

            # Process the QASM 3.0 string line by line for more precise handling
            lines = qasm_string.strip().split('\n')
            processed_lines = []

            # Track if we're dealing with array-style declarations
            array_style_qubits = False
            array_style_bits = False
            qubit_count = 2  # Default, will be updated if found
            bit_count = 2  # Default, will be updated if found

            for line in lines:
                line = line.strip()

                # Handle version
                if "OPENQASM 3.0" in line:
                    processed_lines.append("OPENQASM 2.0;")
                    processed_lines.append('include "qelib1.inc";')
                    continue

                # Handle qubit declarations
                if line.startswith("qubit["):
                    array_style_qubits = True
                    # Extract the count of qubits
                    try:
                        qubit_count = int(line.split('[')[1].split(']')[0])
                        processed_lines.append(f"qreg q[{qubit_count}];")
                    except (IndexError, ValueError):
                        processed_lines.append("qreg q[2];")  # Fallback
                    continue

                if line.startswith("qubit "):
                    qubit_name = line.replace("qubit ", "").replace(";", "")
                    processed_lines.append(f"qreg {qubit_name}[1];")
                    continue

                # Handle bit declarations
                if line.startswith("bit["):
                    array_style_bits = True
                    # Extract the count of bits
                    try:
                        bit_count = int(line.split('[')[1].split(']')[0])
                        processed_lines.append(f"creg c[{bit_count}];")
                    except (IndexError, ValueError):
                        processed_lines.append("creg c[2];")  # Fallback
                    continue

                if line.startswith("bit "):
                    bit_name = line.replace("bit ", "").replace(";", "")
                    processed_lines.append(f"creg {bit_name}[1];")
                    continue

                # Handle measurement syntax
                if " = measure " in line:
                    parts = line.split(" = measure ")
                    if len(parts) == 2:
                        target = parts[0].strip()
                        source = parts[1].strip().replace(";", "")
                        processed_lines.append(f"measure {source} -> {target};")
                    continue

                # For gates and other operations, pass through
                processed_lines.append(line)

            processed_qasm = '\n'.join(processed_lines)
            return processed_qasm

        # Already QASM 2.0 - just ensure the include statement
        if "OPENQASM 2.0" in qasm_string and "include \"qelib1.inc\"" not in qasm_string:
            lines = qasm_string.strip().split('\n')
            for i, line in enumerate(lines):
                if "OPENQASM 2.0" in line:
                    lines.insert(i + 1, 'include "qelib1.inc";')
                    break
            return '\n'.join(lines)

        return qasm_string

    def format_counts(self, counts):
        """
        Format counts for API response.

        Args:
            counts: Dictionary of measurement results from Qiskit

        Returns:
            Dict formatted according to API specifications
        """
        if not counts:
            return {}

        formatted_counts = {}

        for bitstring, count in counts.items():
            try:
                decimal_key = str(int(bitstring, 2))
                formatted_counts[decimal_key] = count
            except ValueError:
                logger.warning(f"Non-binary measurement result: {bitstring}")
                formatted_counts[bitstring] = count

        return formatted_counts

    def get_result_from_qasm(self, qasm_string):
        """
        Wrapper method to get the result object from a QASM string.

        Args:
            qasm_string: String containing QASM representation of a quantum circuit

        Returns:
            Result object containing the measurement results or error
        """
        return self.execute_qasm(qasm_string)


# Example usage
import logging
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

logger = logging.getLogger(__name__)


class QuantumCircuitService:
    """
    Service for creating, executing, and processing quantum circuits.
    """

    def __init__(self, shots=1024):
        """
        Initialize the quantum circuit service.

        Args:
            shots: Number of shots for quantum circuit execution
        """
        self.shots = shots
        self.simulator = AerSimulator()
        logger.info(f"Initialized QuantumCircuitService with {shots} shots")

    def execute_qasm(self, qasm_string):
        """
        Execute a quantum circuit from QASM string.

        Args:
            qasm_string: String containing QASM representation of a quantum circuit

        Returns:
            Dict containing the measurement results or error
        """
        if not qasm_string or not isinstance(qasm_string, str):
            logger.error("Invalid QASM input: empty or not a string")
            return {
                "error": True,
                "message": "Invalid input: QASM must be a non-empty string",
                "error_type": "INPUT_ERROR",
                "details": {"received_type": str(type(qasm_string))}
            }

        # Check for syntax markers
        if "OPENQASM" not in qasm_string:
            logger.error("Missing OPENQASM version declaration")
            return {
                "error": True,
                "message": "Invalid QASM: Missing OPENQASM version declaration",
                "error_type": "SYNTAX_ERROR",
                "details": {"hint": "QASM should start with OPENQASM version declaration"}
            }

        try:
            # Validate QASM version
            version_line = next((line for line in qasm_string.split("\n") if "OPENQASM" in line), None)
            if version_line:
                if "3.0" in version_line:
                    logger.info("Detected QASM 3.0 format")
                elif "2.0" in version_line:
                    logger.info("Detected QASM 2.0 format")
                else:
                    unsupported_version = version_line.split("OPENQASM")[1].strip().split(";")[0].strip()
                    logger.warning(f"Unsupported QASM version: {unsupported_version}")
                    return {
                        "error": True,
                        "message": f"Unsupported QASM version: {unsupported_version}. Only versions 2.0 and 3.0 are supported.",
                        "error_type": "VERSION_ERROR",
                        "details": {"supported_versions": ["2.0", "3.0"]}
                    }

            # Process the QASM string
            processed_qasm = self._preprocess_qasm(qasm_string)
            logger.info(f"Processed QASM string:\n{processed_qasm}")

            # Parse into a quantum circuit
            try:
                circuit = QuantumCircuit.from_qasm_str(processed_qasm)
                logger.info(f"Successfully parsed QASM string into circuit with {circuit.num_qubits} qubits")
            except Exception as parsing_error:
                logger.error(f"Circuit parsing error: {str(parsing_error)}")
                return {
                    "error": True,
                    "message": f"Failed to parse QASM: {str(parsing_error)}",
                    "error_type": "PARSING_ERROR",
                    "details": {
                        "processed_qasm": processed_qasm,
                        "original_error": str(parsing_error)
                    }
                }

            # Validate circuit
            if circuit.num_qubits == 0:
                logger.error("Invalid circuit: No qubits defined")
                return {
                    "error": True,
                    "message": "Invalid circuit: No qubits defined",
                    "error_type": "CIRCUIT_ERROR",
                    "details": {"hint": "Make sure to define qubit registers in your QASM"}
                }

            if not circuit.data:
                logger.warning("Empty circuit: No gates or operations")
                return {
                    "error": True,
                    "message": "Empty circuit: No gates or operations defined",
                    "error_type": "EMPTY_CIRCUIT",
                    "details": {"hint": "Add quantum operations to your circuit"}
                }

            # Check for measurement operations
            has_measurements = any(instr.operation.name == 'measure' for instr in circuit.data)
            if not has_measurements:
                logger.warning("No measurement operations in circuit")
                return {
                    "error": True,
                    "message": "No measurement operations in circuit",
                    "error_type": "NO_MEASUREMENTS",
                    "details": {"hint": "Add measurement operations to get results"}
                }

            # Execute the circuit
            try:
                result = self.simulator.run(circuit, shots=self.shots).result()

                if not result.success:
                    logger.error(f"Simulation failed: {result.status}")
                    return {
                        "error": True,
                        "message": f"Simulation failed: {result.status}",
                        "error_type": "SIMULATION_ERROR",
                        "details": {"status": result.status}
                    }

                counts = result.get_counts(circuit)
                logger.info(f"Circuit execution complete with {len(counts)} unique outcomes")
                formatted_counts = self.format_counts(counts)

                # Add some statistics to the output
                total_shots = sum(formatted_counts.values())
                most_frequent = max(formatted_counts.items(), key=lambda x: x[1]) if formatted_counts else None

                return {
                    "error": False,
                    "counts": formatted_counts,
                    "statistics": {
                        "total_shots": total_shots,
                        "unique_outcomes": len(formatted_counts),
                        "most_frequent": {
                            "state": most_frequent[0] if most_frequent else None,
                            "count": most_frequent[1] if most_frequent else 0,
                            "probability": round(most_frequent[1] / total_shots, 4) if most_frequent else 0
                        }
                    }
                }

            except Exception as simulation_error:
                logger.error(f"Simulation error: {str(simulation_error)}")
                return {
                    "error": True,
                    "message": f"Simulation error: {str(simulation_error)}",
                    "error_type": "SIMULATION_ERROR",
                    "details": {"original_error": str(simulation_error)}
                }

        except Exception as e:
            logger.error(f"Unexpected error processing QASM: {str(e)}")
            return {
                "error": True,
                "message": f"Unexpected error: {str(e)}",
                "error_type": "UNEXPECTED_ERROR",
                "details": {"exception_type": type(e).__name__}
            }

    def _preprocess_qasm(self, qasm_string):
        """
        Preprocess QASM string to ensure compatibility.

        Args:
            qasm_string: Input QASM string

        Returns:
            Processed QASM string or raises detailed exceptions for invalid syntax
        """
        # Initial validation
        if not qasm_string.strip():
            raise ValueError("Empty QASM string")

        # Handle QASM 3.0 to 2.0 conversion
        if "OPENQASM 3.0" in qasm_string:
            logger.info("Converting QASM 3.0 to QASM 2.0 format")

            # Process the QASM 3.0 string line by line for more precise handling
            lines = qasm_string.strip().split('\n')
            processed_lines = []

            # Track registers and their types
            registers = {}
            qubit_registers = set()
            bit_registers = set()
            gate_definitions = set()

            # Track line numbers for better error reporting
            line_number = 0

            for line in lines:
                line_number += 1
                line = line.strip()

                if not line or line.startswith("//"):
                    # Skip empty lines and comments
                    continue

                # Handle version
                if "OPENQASM 3.0" in line:
                    processed_lines.append("OPENQASM 2.0;")
                    processed_lines.append('include "qelib1.inc";')
                    continue

                # Track custom gate definitions
                if line.startswith("gate "):
                    try:
                        gate_name = line.split("gate ")[1].split(" ")[0]
                        gate_definitions.add(gate_name)
                        processed_lines.append(line)
                        continue
                    except Exception as e:
                        logger.warning(f"Failed to parse gate definition at line {line_number}: {line}")
                        processed_lines.append(line)  # Keep it as is and let Qiskit handle any error
                        continue

                # Handle qubit array declarations
                if line.startswith("qubit["):
                    try:
                        parts = line.split("qubit[")[1].split("]")
                        count = int(parts[0])
                        name_part = parts[1].strip()

                        # Handle trailing semicolon and extract name
                        if name_part.endswith(";"):
                            name_part = name_part[:-1].strip()

                        register_name = name_part if name_part else "q"
                        qubit_registers.add(register_name)
                        registers[register_name] = {"type": "qubit", "size": count}

                        processed_lines.append(f"qreg {register_name}[{count}];")
                    except Exception as e:
                        logger.error(f"Error parsing qubit array declaration at line {line_number}: {str(e)}")
                        raise ValueError(f"Invalid qubit array syntax at line {line_number}: {line}")
                    continue

                # Handle single qubit declarations
                if line.startswith("qubit "):
                    try:
                        name_part = line.replace("qubit ", "").strip()

                        # Handle trailing semicolon and extract name
                        if name_part.endswith(";"):
                            name_part = name_part[:-1].strip()

                        qubit_registers.add(name_part)
                        registers[name_part] = {"type": "qubit", "size": 1}

                        processed_lines.append(f"qreg {name_part}[1];")
                    except Exception as e:
                        logger.error(f"Error parsing single qubit declaration at line {line_number}: {str(e)}")
                        raise ValueError(f"Invalid qubit declaration syntax at line {line_number}: {line}")
                    continue

                # Handle bit array declarations
                if line.startswith("bit["):
                    try:
                        parts = line.split("bit[")[1].split("]")
                        count = int(parts[0])
                        name_part = parts[1].strip()

                        # Handle trailing semicolon and extract name
                        if name_part.endswith(";"):
                            name_part = name_part[:-1].strip()

                        register_name = name_part if name_part else "c"
                        bit_registers.add(register_name)
                        registers[register_name] = {"type": "bit", "size": count}

                        processed_lines.append(f"creg {register_name}[{count}];")
                    except Exception as e:
                        logger.error(f"Error parsing bit array declaration at line {line_number}: {str(e)}")
                        raise ValueError(f"Invalid bit array syntax at line {line_number}: {line}")
                    continue

                # Handle single bit declarations
                if line.startswith("bit "):
                    try:
                        name_part = line.replace("bit ", "").strip()

                        # Handle trailing semicolon and extract name
                        if name_part.endswith(";"):
                            name_part = name_part[:-1].strip()

                        bit_registers.add(name_part)
                        registers[name_part] = {"type": "bit", "size": 1}

                        processed_lines.append(f"creg {name_part}[1];")
                    except Exception as e:
                        logger.error(f"Error parsing single bit declaration at line {line_number}: {str(e)}")
                        raise ValueError(f"Invalid bit declaration syntax at line {line_number}: {line}")
                    continue

                # Handle QASM 3.0 measurement syntax
                if " = measure " in line:
                    try:
                        parts = line.split(" = measure ")
                        if len(parts) == 2:
                            target = parts[0].strip()
                            source = parts[1].strip()

                            # Handle trailing semicolon
                            if source.endswith(";"):
                                source = source[:-1].strip()

                            # Validate that both registers exist
                            if target not in bit_registers and not any(r in target for r in bit_registers):
                                logger.warning(
                                    f"Target register '{target}' in measurement not declared as bit register")

                            if source not in qubit_registers and not any(r in source for r in qubit_registers):
                                logger.warning(
                                    f"Source register '{source}' in measurement not declared as qubit register")

                            processed_lines.append(f"measure {source} -> {target};")
                        else:
                            logger.error(f"Invalid measurement syntax at line {line_number}")
                            raise ValueError(f"Invalid measurement syntax at line {line_number}: {line}")
                    except Exception as e:
                        logger.error(f"Error parsing measurement at line {line_number}: {str(e)}")
                        raise ValueError(f"Error in measurement syntax at line {line_number}: {line}")
                    continue

                # Handle comments
                if "//" in line and not line.startswith("//"):
                    # Preserve inline comments but after proper conversion
                    content_part = line.split("//")[0].strip()
                    comment_part = "//" + "//".join(line.split("//")[1:])

                    # Process the content part
                    if "=" in content_part and not any(op in content_part for op in ["==", ">=", "<="]):
                        # This might be a variable assignment, not supported in QASM 2.0
                        logger.warning(f"Variable assignment detected at line {line_number}, not supported in QASM 2.0")
                        # Skip this line for now
                        continue

                    processed_lines.append(f"{content_part} {comment_part}")
                    continue

                # Handle pragma directives
                if "pragma" in line:
                    logger.info(f"Found pragma directive at line {line_number}, passing through")
                    processed_lines.append(line)
                    continue

                # Check for unsupported QASM 3.0 features
                problematic_features = [
                    ("for", "loops"),
                    ("while", "loops"),
                    ("if", "conditional statements"),
                    ("else", "conditional statements"),
                    ("return", "functions"),
                    ("def", "function definitions"),
                    ("import", "imports"),
                    ("export", "exports"),
                    ("using", "using statements"),
                    ("input", "classical input")
                ]

                for keyword, feature_name in problematic_features:
                    if keyword in line.split() or f"{keyword}(" in line:
                        logger.warning(
                            f"QASM 3.0 {feature_name} at line {line_number} are not supported in conversion to QASM 2.0")
                        # We'll include the line but it will likely cause errors in Qiskit

                # For gates and other operations, pass through
                processed_lines.append(line)

            # If no registers were found, add default ones
            if not any(reg["type"] == "qubit" for reg in registers.values()):
                logger.warning("No qubit registers found, adding default 'qreg q[2];'")
                processed_lines.insert(2, "qreg q[2];")

            if not any(reg["type"] == "bit" for reg in registers.values()):
                logger.warning("No bit registers found, adding default 'creg c[2];'")
                processed_lines.insert(3, "creg c[2];")

            # Check if there are any measurement operations
            if not any("measure" in line for line in processed_lines):
                logger.warning("No measurement operations found in the circuit")

            processed_qasm = '\n'.join(processed_lines)
            return processed_qasm

        # Already QASM 2.0 - just ensure the include statement
        if "OPENQASM 2.0" in qasm_string:
            if "include \"qelib1.inc\"" not in qasm_string:
                lines = qasm_string.strip().split('\n')
                include_added = False

                for i, line in enumerate(lines):
                    if "OPENQASM 2.0" in line:
                        lines.insert(i + 1, 'include "qelib1.inc";')
                        include_added = True
                        break

                if include_added:
                    qasm_string = '\n'.join(lines)

            # Basic validation of QASM 2.0
            if "qreg" not in qasm_string:
                logger.warning("No quantum registers (qreg) found in QASM 2.0 code")

            if "creg" not in qasm_string and "measure" in qasm_string:
                logger.warning("Measurements present but no classical registers (creg) found")

            if "measure" not in qasm_string:
                logger.warning("No measurement operations found in the circuit")

            return qasm_string

        # If we got here, we have an unknown version
        if "OPENQASM" in qasm_string:
            version_line = next((line for line in qasm_string.split("\n") if "OPENQASM" in line), None)
            version = version_line.split("OPENQASM")[1].strip().split(";")[0].strip() if version_line else "unknown"
            logger.error(f"Unsupported QASM version: {version}")
            raise ValueError(f"Unsupported QASM version: {version}. Only versions 2.0 and 3.0 are supported.")
        else:
            logger.error("Missing OPENQASM version declaration")
            raise ValueError("Invalid QASM: Missing OPENQASM version declaration")

        return qasm_string

    def format_counts(self, counts):
        """
        Format counts for API response.

        Args:
            counts: Dictionary of measurement results from Qiskit

        Returns:
            Dict formatted according to API specifications
        """
        if not counts:
            return {}

        formatted_counts = {}

        for bitstring, count in counts.items():
            try:
                decimal_key = str(int(bitstring, 2))
                formatted_counts[decimal_key] = count
            except ValueError:
                logger.warning(f"Non-binary measurement result: {bitstring}")
                formatted_counts[bitstring] = count

        return formatted_counts

    def get_result_from_qasm(self, qasm_string):
        """
        Wrapper method to get the result object from a QASM string.

        Args:
            qasm_string: String containing QASM representation of a quantum circuit

        Returns:
            Result object containing the measurement results or error
        """
        return self.execute_qasm(qasm_string)


# Example usage
if __name__ == "__main__":
    service = QuantumCircuitService()

    # Bell state circuit in QASM 3.0 format
    bell_qasm_3 = """
OPENQASM 3.0;
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
"""

    # Test with more complex QASM 3.0 examples
    ghz_qasm_3 = """
OPENQASM 3.0;
qubit[3] q;
bit[3] c;
h q[0];
cx q[0], q[1];
cx q[1], q[2];
c = measure q;
"""

    # Test case with missing measurement
    missing_measurement_qasm = """
OPENQASM 3.0;
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
"""

    # Test case with syntax error (missing semicolon)
    syntax_error_qasm = """
OPENQASM 3.0;
qubit[2] q;
bit[2] c;
h q[0]
cx q[0], q[1];
c = measure q;
"""

    # Test case with unsupported QASM 3.0 features
    unsupported_features_qasm = """
OPENQASM 3.0;
qubit[2] q;
bit[2] c;
for i in [0:1] {
  h q[i];
}
cx q[0], q[1];
c = measure q;
"""

    # Test case with invalid register reference
    invalid_register_qasm = """
OPENQASM 3.0;
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[3];
c = measure q;
"""

    # Multi-qubit circuit with controlled operations
    toffoli_qasm = """
OPENQASM 3.0;
qubit[3] q;
bit[3] c;
h q[2];
cx q[1], q[2];
tdg q[2];
cx q[0], q[2];
t q[2];
cx q[1], q[2];
tdg q[2];
cx q[0], q[2];
t q[1];
t q[2];
h q[2];
cx q[0], q[1];
t q[0];
tdg q[1];
cx q[0], q[1];
c = measure q;
"""

    print("\n===== Testing Basic Circuits =====")
    result1 = service.get_result_from_qasm(bell_qasm_3)
    print("Bell State Result:", result1)

    result2 = service.get_result_from_qasm(ghz_qasm_3)
    print("GHZ State Result:", result2)

    print("\n===== Testing Error Cases =====")
    print("Missing Measurement Error:", service.get_result_from_qasm(missing_measurement_qasm))
    print("Syntax Error:", service.get_result_from_qasm(syntax_error_qasm))
    print("Unsupported Features Error:", service.get_result_from_qasm(unsupported_features_qasm))
    print("Invalid Register Error:", service.get_result_from_qasm(invalid_register_qasm))

    print("\n===== Testing Advanced Circuit =====")
    print("Toffoli Circuit Result:", service.get_result_from_qasm(toffoli_qasm))