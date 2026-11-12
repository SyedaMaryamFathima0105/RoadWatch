package org.roadwatch.api;
import org.springframework.web.bind.annotation.*;import org.springframework.http.*;import java.util.*;
@RestControllerAdvice public class ErrorHandler {
 @ExceptionHandler(IllegalArgumentException.class)public ResponseEntity<?> bad(IllegalArgumentException e){return ResponseEntity.badRequest().body(Map.of("error",e.getMessage()));}
 @ExceptionHandler(NoSuchElementException.class)public ResponseEntity<?> missing(NoSuchElementException e){return ResponseEntity.status(404).body(Map.of("error",e.getMessage()));}
 @ExceptionHandler(org.springframework.web.server.ResponseStatusException.class)public ResponseEntity<?> status(org.springframework.web.server.ResponseStatusException e){return ResponseEntity.status(e.getStatusCode()).body(Map.of("error",e.getReason()==null?"Request failed":e.getReason()));}
 @ExceptionHandler(Exception.class)public ResponseEntity<?> fail(Exception e){return ResponseEntity.status(500).body(Map.of("error","Request failed","detail",String.valueOf(e.getMessage())));}
}
