function testBundle(eid,code){
  var info=exInfo(eid),spec=GRADE[eid];if(!info||!spec)return Promise.reject(new Error("no tests"));
  var dir=eid.replace(/\./g,"_")+"-"+slug(info.e.t),crate="ex_"+eid.toLowerCase().replace(/[^a-z0-9]+/g,"_");
  var body=(code&&code.trim()?code:(spec.starter||""));
  var head="// "+eid+" "+info.e.t+" (Rust Course)\n// "+(spec.mutation?"The code under test is at the top; your tests follow it. cargo test runs them against the real code\n// (the course page also runs them against planted bugs).":"Your code is at the top; the course's hidden tests are in mod grader_tests at the bottom.")+"\n// Run: cargo test        Style notes: cargo clippy --all-targets\n\n";
  var toml="[package]\nname = \""+crate+"\"\nversion = \"0.1.0\"\nedition = \"2024\"\n\n[dependencies]\n\n[lints.rust]\ndead_code = \"allow\"\nunused = \"allow\"\n";
  var readme="# "+eid+" "+info.e.t+"\n\nThis folder is a Cargo project with your answer and "+(spec.mutation?"the code your tests check":"the same tests the course runs")+".\n\n```\ncargo test\n```\n\nEdit `src/lib.rs` until every test passes, then paste your code back into the course page.\nNeeds Rust 1.85 or newer (edition 2024): https://rustup.rs\n";
  return Promise.resolve({name:dir+"-cargo.zip",files:[
    {name:dir+"/Cargo.toml",text:toml},{name:dir+"/README.md",text:readme},
    {name:dir+"/src/lib.rs",text:(head+rsWithTests(eid,body)).replace(/include_str!\("exercise\.rs"\)/g,"include_str!(\"lib.rs\")").replace(/\s*$/,"\n")}]});
}
