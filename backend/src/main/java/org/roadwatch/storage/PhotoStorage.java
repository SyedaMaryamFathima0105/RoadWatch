package org.roadwatch.storage;
import org.springframework.web.multipart.MultipartFile;import java.io.IOException;
/** Storage boundary for local MVP; replace the adapter with MinIO/S3 without changing report logic. */
public interface PhotoStorage { String store(MultipartFile image,String extension)throws IOException; }
