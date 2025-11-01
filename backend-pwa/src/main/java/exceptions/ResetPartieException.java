package exceptions;
public class ResetPartieException extends Exception {
    public ResetPartieException(String message) {
        super(message);
    }
    public ResetPartieException() {
        super("La partie a été réinitialisée.");
    }
}