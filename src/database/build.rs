use protoc_bin_vendored::protoc_bin_path;
use std::{env};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Get the path to the vendored protoc binary.
    let protoc_path = protoc_bin_path().expect("protoc not found");

    // Optionally, print the path for debugging:
    println!("Using protoc from: {:?}", protoc_path);

    unsafe { env::set_var("PROTOC", protoc_path) };

    // Now compile your proto files using tonic_build.
    // tonic_build::configure()
    //     .compile(
    //         &["../protos/database.proto"], // Path to your proto file(s)
    //         &["../protos"],                // Include paths for proto imports
    //     )?;
    tonic_build::compile_protos("../protos/database.proto")?;
    Ok(())
}
