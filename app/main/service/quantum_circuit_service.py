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

            # Replace version
            qasm_string = qasm_string.replace("OPENQASM 3.0", "OPENQASM 2.0")

            # Convert register declarations
            qasm_string = qasm_string.replace("qubit[", "qreg q[")
            qasm_string = qasm_string.replace("bit[", "creg c[")

            # Convert measurement syntax
            qasm_string = qasm_string.replace("c = measure q", "measure q -> c")

            # Specific replacements for common patterns
            qasm_string = qasm_string.replace("qubit q", "qreg q[1]")
            qasm_string = qasm_string.replace("bit c", "creg c[1]")

        # Ensure include statement for QASM 2.0
        if "OPENQASM 2.0" in qasm_string and "include \"qelib1.inc\"" not in qasm_string:
            lines = qasm_string.strip().split('\n')
            include_added = False

            for i, line in enumerate(lines):
                if "OPENQASM 2.0" in line:
                    lines.insert(i + 1, 'include "qelib1.inc";')
                    include_added = True
                    break

            if include_added:
                qasm_string = '\n'.join(lines)

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

    # Bell state circuit in QASM 2.0 format
    bell_qasm_2 = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
measure q -> c;
"""
    result1 = service.get_result_from_qasm(bell_qasm_3)
    result2 = service.get_result_from_qasm(bell_qasm_2)