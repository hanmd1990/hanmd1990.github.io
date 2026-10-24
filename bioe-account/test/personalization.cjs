const {test}=require('node:test');
const assert=require('node:assert/strict');
const {key,rank}=require('../../static/literature-personalization.js');
const paper=(id,title,topics=[],relevance=3)=>({id,title,summary:title,topics,relevance});
const training=paper('old','wireless magnetic implant bioelectronics',['Implants']);
const implant=paper('a','wireless magnetic implant bioelectronics',['Implants']);
const unrelated=paper('b','galaxy astronomy orbital planets',['Astronomy']);
test('earlier report feedback improves the next report for that account',()=>{
 const articles=[unrelated,implant],history=[training,...articles];
 assert.equal(rank(articles,{old:{signals:['more']}},history)[0].id,'a');
 assert.equal(rank(articles,{old:{signals:['irrelevant']}},history)[0].id,'b');
});
test('negative feedback demotes only its paper and retains the whole collection',()=>{
 const out=rank([implant,unrelated],{a:{signals:['irrelevant']}});
 assert.equal(out.length,2);assert.equal(out[1].id,'a');
});
test('neutral account and source inputs stay unchanged',()=>{
 const articles=[implant,unrelated],before=JSON.stringify(articles);rank(articles,{});assert.equal(JSON.stringify(articles),before);
});
test('versioned preprints share feedback identity',()=>{
 assert.equal(key({doi:'https://doi.org/10.21203/rs.3.rs-123/v2'}),'10.21203/rs.3.rs-123');
});
test('personal preference has bounded influence over editorial priority',()=>{
 const high=paper('h','galaxy astronomy',['Astronomy'],10);assert.equal(rank([implant,high],{old:{signals:['more']}},[training,implant,high])[0].id,'h');
});
