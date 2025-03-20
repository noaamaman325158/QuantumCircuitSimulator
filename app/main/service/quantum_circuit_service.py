import logging
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.qasm2.exceptions import QASM2ParseError
from app.main.exceptions.custom_exceptions import QASMParsingError, CircuitExecutionError

logger = logging.getLogger(__name__)

class QuantumCircuitService:
    """
    Service for creating, executing, and processing quantum circuits.
    """

    def __init__(self, shots=10000):
        """
        Initialize the quantum circuit service.

        Args:
            shots: Number of shots for quantum circuit execution
        """
        self.shots = shots
        self.simulator = AerSimulator()
        logger.info(f"Initialized QuantumCircuitService with {shots} shots")

    async def execute_qasm(self, qasm_string):
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
            job = self.simulator.run(circuit, shots=self.shots)
            result = job.result()  # This should be called synchronously
            counts = result.get_counts(circuit)

            logger.info(f"Circuit execution complete with {len(counts)} unique outcomes")
            formatted_counts = self.format_counts(counts)
            return {"error": False, "counts": formatted_counts}

        except QASM2ParseError as e:
            logger.error(f"QASM parsing failed. Error: {str(e)}")
            raise QASMParsingError(message=str(e))
        except QASMParsingError as e:
            logger.error(f"QASM parsing failed. Error: {str(e)}")
            return {"error": True, "message": str(e)}
        except CircuitExecutionError as e:
            logger.error(f"Circuit execution failed. Error: {str(e)}")
            return {"error": True, "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise CircuitExecutionError(message=str(e))

    def _preprocess_qasm(self, qasm_string):
        """
        Preprocess QASM string to ensure compatibility.

        Args:
            qasm_string: Input QASM string

        Returns:
            Processed QASM string
        """
        try:
            # Handle QASM 3.0 to 2.0 conversion
            if "OPENQASM 3.0" in qasm_string:
                logger.info("Converting QASM 3.0 to QASM 2.0 format")

                # Process the QASM 3.0 string line by line for more precise handling
                lines = qasm_string.strip().split('\n')
                processed_lines = []

                for line in lines:
                    line = line.strip()

                    # Handle version
                    if "OPENQASM 3.0" in line:
                        processed_lines.append("OPENQASM 2.0;")
                        processed_lines.append('include "qelib1.inc";')
                        continue

                    # Handle qubit and bit declarations
                    if line.startswith("qubit[") or line.startswith("bit["):
                        line = line.replace("qubit[", "qreg q[").replace("bit[", "creg c[")

                    # Handle measurement syntax
                    if " = measure " in line:
                        line = line.replace(" = measure ", " measure ")

                    processed_lines.append(line)

                processed_qasm = '\n'.join(processed_lines)
                return processed_qasm

            # Already QASM 2.0 - just ensure the include statement
            if "OPENQASM 2.0" in qasm_string and 'include "qelib1.inc"' not in qasm_string:
                lines = qasm_string.strip().split('\n')
                for i, line in enumerate(lines):
                    if "OPENQASM 2.0" in line:
                        lines.insert(i + 1, 'include "qelib1.inc";')
                        break
                return '\n'.join(lines)

            return qasm_string

        except Exception as e:
            raise QASMParsingError(message=str(e), original_qasm=qasm_string)

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
cx q[0], q[1];"""
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