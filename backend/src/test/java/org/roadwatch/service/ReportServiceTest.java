package org.roadwatch.service;
import org.junit.jupiter.api.Test;import static org.junit.jupiter.api.Assertions.*;
class ReportServiceTest {
 @Test void haversineIsZeroForSamePoint(){assertEquals(0,ReportService.distance(19.07,72.87,19.07,72.87),0.001);}
 @Test void haversineMeasuresApproximateThirtyMetres(){double d=ReportService.distance(0,0,0,0.00027);assertTrue(d>29&&d<31);}
}
