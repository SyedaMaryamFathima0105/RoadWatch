package org.roadwatch.storage;
import org.springframework.beans.factory.annotation.Value;import org.springframework.stereotype.Service;import org.springframework.web.multipart.MultipartFile;import java.io.IOException;import java.nio.file.*;import java.util.UUID;
@Service public class LocalPhotoStorage implements PhotoStorage {
 @Value("${roadwatch.upload-dir}")String uploadDir;
 @Override public String store(MultipartFile image,String extension)throws IOException{String name=UUID.randomUUID()+extension;Path dir=Path.of(uploadDir).toAbsolutePath();Files.createDirectories(dir);Files.copy(image.getInputStream(),dir.resolve(name),StandardCopyOption.REPLACE_EXISTING);return "/uploads/"+name;}
}
